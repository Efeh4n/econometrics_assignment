# -*- coding: utf-8 -*-
"""
IST3102 Ekonometri Proje - TÜFE Enflasyon Analizi
Kapsamlı Ekonometrik Analiz Scripti

Bağımlı Değişken: TÜFE (Enflasyon)
Bağımsız Değişkenler:
  X1: USD Dolar Kuru
  X2: Sanayi Üretim Endeksi
  X3: M3 Para Piyasaları
  X4: Tüketici Güven Endeksi

Dönem: 2015:04 - 2023:07 (100 aylık gözlem)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_white, het_goldfeldquandt
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
import warnings
import os
import json

warnings.filterwarnings('ignore')

# ============================================================
# AYARLAR
# ============================================================
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

ALPHA = 0.05  # Anlamlılık düzeyi
OUTPUT_DIR = 'grafikler'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sonuçları saklamak için
results_text = []

def log_result(text):
    """Sonucu hem ekrana yazdır hem de kaydet."""
    print(text)
    results_text.append(text)

def separator(title=""):
    line = "=" * 80
    log_result(f"\n{line}")
    if title:
        log_result(f"  {title}")
        log_result(line)

# ============================================================
# 1. VERİ OKUMA VE HAZIRLAMA
# ============================================================
separator("1. VERİ OKUMA VE HAZIRLAMA")

df = pd.read_excel('Enflasyon verileri1.xlsx', sheet_name='Sayfa1')

# Tarih sütununu datetime'a çevir
df['Tarih'] = pd.to_datetime(df['Tarih'])
df = df.set_index('Tarih')
df = df.sort_index()

# Kullanılacak değişkenleri seç ve yeniden adlandır
variables = {
    'tüfe': 'tufe',
    'USD Dolar': 'usd',
    'Sanayi Üretim Endeksi (2015=100))': 'sanayi',
    'M3 Para piyasaları': 'm3',
    'Tüketici Güven Endeksi (Mevsimsellikten Arındırılmamış)': 'tuketici_guven'
}

# Sütun adlarını kontrol et ve eşleştir
col_mapping = {}
for original, new_name in variables.items():
    # Case insensitive eşleştirme
    for col in df.columns:
        if original.lower() == col.lower().strip():
            col_mapping[col] = new_name
            break

data = df[list(col_mapping.keys())].rename(columns=col_mapping)

# M3'ü milyar TL'ye çevir (daha okunabilir olması için)
data['m3'] = data['m3'] / 1e9

log_result(f"\nVeri Seti Bilgileri:")
log_result(f"  Dönem: {data.index[0].strftime('%Y-%m')} - {data.index[-1].strftime('%Y-%m')}")
log_result(f"  Gözlem Sayısı: {len(data)}")
log_result(f"  Değişken Sayısı: {len(data.columns)}")
log_result(f"\nDeğişkenler:")
log_result(f"  Y  (Bağımlı)  : TÜFE (Tüketici Fiyat Endeksi)")
log_result(f"  X1 (Bağımsız) : USD Dolar Kuru")
log_result(f"  X2 (Bağımsız) : Sanayi Üretim Endeksi (2015=100)")
log_result(f"  X3 (Bağımsız) : M3 Para Piyasaları (Milyar TL)")
log_result(f"  X4 (Bağımsız) : Tüketici Güven Endeksi")

# Eksik veri kontrolü
missing = data.isnull().sum()
if missing.sum() > 0:
    log_result(f"\nEksik Veriler:")
    for col, cnt in missing.items():
        if cnt > 0:
            log_result(f"  {col}: {cnt} eksik gözlem")
    data = data.dropna()
    log_result(f"  Eksik veriler temizlendi. Kalan gözlem: {len(data)}")
else:
    log_result(f"\n  Eksik veri bulunmamaktadır.")

# ============================================================
# TANIMLAYICI İSTATİSTİKLER
# ============================================================
separator("TANIMLAYICI İSTATİSTİKLER")

desc_stats = data.describe().T
desc_stats['cv'] = (desc_stats['std'] / desc_stats['mean']) * 100  # Değişim katsayısı
desc_stats['range'] = desc_stats['max'] - desc_stats['min']

var_labels = {
    'tufe': 'TÜFE',
    'usd': 'USD Dolar',
    'sanayi': 'Sanayi Üretim End.',
    'm3': 'M3 (Milyar TL)',
    'tuketici_guven': 'Tüketici Güven End.'
}

log_result(f"\n{'Değişken':<22} {'Ort.':<12} {'Std.Sap.':<12} {'Min':<12} {'Max':<12} {'CV(%)':<10} {'Çarpıklık':<10}")
log_result("-" * 90)
for var in data.columns:
    mean = desc_stats.loc[var, 'mean']
    std = desc_stats.loc[var, 'std']
    mn = desc_stats.loc[var, 'min']
    mx = desc_stats.loc[var, 'max']
    cv = desc_stats.loc[var, 'cv']
    skew = data[var].skew()
    log_result(f"{var_labels[var]:<22} {mean:<12.4f} {std:<12.4f} {mn:<12.4f} {mx:<12.4f} {cv:<10.2f} {skew:<10.4f}")

# Korelasyon Matrisi
separator("KORELASYON MATRİSİ")
corr = data.corr()
log_result(f"\n{corr.round(4).to_string()}")

# ============================================================
# 2. DEĞİŞKENLERİN GRAFİKLERİ
# ============================================================
separator("2. DEĞİŞKENLERİN GRAFİKLERİ")

colors = {
    'tufe': '#E74C3C',
    'usd': '#2ECC71',
    'sanayi': '#3498DB',
    'm3': '#9B59B6',
    'tuketici_guven': '#F39C12'
}

titles = {
    'tufe': 'TÜFE (Tüketici Fiyat Endeksi)',
    'usd': 'USD/TRY Dolar Kuru',
    'sanayi': 'Sanayi Üretim Endeksi (2015=100)',
    'm3': 'M3 Para Piyasaları (Milyar TL)',
    'tuketici_guven': 'Tüketici Güven Endeksi'
}

ylabels = {
    'tufe': 'TÜFE Değeri',
    'usd': 'TL/USD',
    'sanayi': 'Endeks (2015=100)',
    'm3': 'Milyar TL',
    'tuketici_guven': 'Endeks Değeri'
}

# Her değişken için ayrı grafik
for var in data.columns:
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(data.index, data[var], color=colors[var], linewidth=2, label=titles[var])
    ax.fill_between(data.index, data[var], alpha=0.1, color=colors[var])
    ax.set_title(f'{titles[var]} (2015-2023)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Tarih', fontsize=12)
    ax.set_ylabel(ylabels[var], fontsize=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    plt.xticks(rotation=45)
    ax.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/{var}_zaman_serisi.png', dpi=150, bbox_inches='tight')
    plt.close()
    log_result(f"  ✓ {titles[var]} grafiği kaydedildi.")

# Tüm değişkenler bir arada (alt alta)
fig, axes = plt.subplots(5, 1, figsize=(14, 20), sharex=True)
for i, var in enumerate(data.columns):
    axes[i].plot(data.index, data[var], color=colors[var], linewidth=2)
    axes[i].fill_between(data.index, data[var], alpha=0.1, color=colors[var])
    axes[i].set_title(titles[var], fontsize=12, fontweight='bold')
    axes[i].set_ylabel(ylabels[var], fontsize=10)
    axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
axes[-1].set_xlabel('Tarih', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/tum_degiskenler.png', dpi=150, bbox_inches='tight')
plt.close()
log_result(f"  ✓ Tüm değişkenler grafiği kaydedildi.")

# Korelasyon ısı haritası
fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(corr.values, cmap='RdYlBu_r', vmin=-1, vmax=1, aspect='auto')
ax.set_xticks(range(len(corr.columns)))
ax.set_yticks(range(len(corr.columns)))
ax.set_xticklabels([var_labels[v] for v in corr.columns], rotation=45, ha='right')
ax.set_yticklabels([var_labels[v] for v in corr.columns])
for i in range(len(corr)):
    for j in range(len(corr)):
        color = 'white' if abs(corr.values[i, j]) > 0.5 else 'black'
        ax.text(j, i, f'{corr.values[i, j]:.3f}', ha='center', va='center', color=color, fontsize=10)
plt.colorbar(im, ax=ax, label='Korelasyon Katsayısı')
ax.set_title('Korelasyon Matrisi', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/korelasyon_matrisi.png', dpi=150, bbox_inches='tight')
plt.close()
log_result(f"  ✓ Korelasyon matrisi grafiği kaydedildi.")

# ============================================================
# 3. FONKSİYONEL FORM KARŞILAŞTIRMASI
# ============================================================
separator("3. FONKSİYONEL FORM KARŞILAŞTIRMASI")

Y = data['tufe']
X_vars = data[['usd', 'sanayi', 'm3', 'tuketici_guven']]

# Logaritmik dönüşümler
lnY = np.log(Y)
lnX = np.log(X_vars)

model_results = {}

# Model 1: Lin-Lin
log_result("\n--- Model 1: Lin-Lin ---")
log_result("  Y = β₀ + β₁·USD + β₂·Sanayi + β₃·M3 + β₄·TüketiciGüven + ε")
X_linlin = sm.add_constant(X_vars)
model_linlin = sm.OLS(Y, X_linlin).fit()
model_results['Lin-Lin'] = model_linlin
log_result(f"  R² = {model_linlin.rsquared:.6f}")
log_result(f"  Düzeltilmiş R² = {model_linlin.rsquared_adj:.6f}")
log_result(f"  AIC = {model_linlin.aic:.4f}")
log_result(f"  BIC = {model_linlin.bic:.4f}")
log_result(f"  F-ist = {model_linlin.fvalue:.4f}, p = {model_linlin.f_pvalue:.6f}")

# Model 2: Log-Log
log_result("\n--- Model 2: Log-Log ---")
log_result("  lnY = β₀ + β₁·lnUSD + β₂·lnSanayi + β₃·lnM3 + β₄·lnTüketiciGüven + ε")
X_loglog = sm.add_constant(lnX)
model_loglog = sm.OLS(lnY, X_loglog).fit()
model_results['Log-Log'] = model_loglog
log_result(f"  R² = {model_loglog.rsquared:.6f}")
log_result(f"  Düzeltilmiş R² = {model_loglog.rsquared_adj:.6f}")
log_result(f"  AIC = {model_loglog.aic:.4f}")
log_result(f"  BIC = {model_loglog.bic:.4f}")
log_result(f"  F-ist = {model_loglog.fvalue:.4f}, p = {model_loglog.f_pvalue:.6f}")

# Model 3: Log-Lin (Semi-log)
log_result("\n--- Model 3: Log-Lin (Semi-log) ---")
log_result("  lnY = β₀ + β₁·USD + β₂·Sanayi + β₃·M3 + β₄·TüketiciGüven + ε")
X_loglin = sm.add_constant(X_vars)
model_loglin = sm.OLS(lnY, X_loglin).fit()
model_results['Log-Lin'] = model_loglin
log_result(f"  R² = {model_loglin.rsquared:.6f}")
log_result(f"  Düzeltilmiş R² = {model_loglin.rsquared_adj:.6f}")
log_result(f"  AIC = {model_loglin.aic:.4f}")
log_result(f"  BIC = {model_loglin.bic:.4f}")
log_result(f"  F-ist = {model_loglin.fvalue:.4f}, p = {model_loglin.f_pvalue:.6f}")

# Model 4: Lin-Log
log_result("\n--- Model 4: Lin-Log ---")
log_result("  Y = β₀ + β₁·lnUSD + β₂·lnSanayi + β₃·lnM3 + β₄·lnTüketiciGüven + ε")
X_linlog = sm.add_constant(lnX)
model_linlog = sm.OLS(Y, X_linlog).fit()
model_results['Lin-Log'] = model_linlog
log_result(f"  R² = {model_linlog.rsquared:.6f}")
log_result(f"  Düzeltilmiş R² = {model_linlog.rsquared_adj:.6f}")
log_result(f"  AIC = {model_linlog.aic:.4f}")
log_result(f"  BIC = {model_linlog.bic:.4f}")
log_result(f"  F-ist = {model_linlog.fvalue:.4f}, p = {model_linlog.f_pvalue:.6f}")

# Karşılaştırma tablosu
log_result("\n--- Fonksiyonel Form Karşılaştırma Tablosu ---")
log_result(f"{'Model':<15} {'R²':<12} {'Adj.R²':<12} {'AIC':<14} {'BIC':<14} {'F-ist':<12}")
log_result("-" * 75)
for name, model in model_results.items():
    log_result(f"{name:<15} {model.rsquared:<12.6f} {model.rsquared_adj:<12.6f} {model.aic:<14.4f} {model.bic:<14.4f} {model.fvalue:<12.4f}")

# En iyi modeli belirle (AIC'ye göre - aynı bağımlı değişkene sahip modeller arasında)
# Not: Lin-Lin ve Lin-Log (Y bağımlı); Log-Log ve Log-Lin (lnY bağımlı) kendi aralarında karşılaştırılır
log_result("\n  Not: R² karşılaştırması yalnızca aynı bağımlı değişkene sahip modeller arasında geçerlidir.")
log_result("  Lin-Lin vs Lin-Log (Bağımlı: Y) ve Log-Log vs Log-Lin (Bağımlı: lnY) karşılaştırılabilir.")

# Y bağımlı modeller
y_models = {'Lin-Lin': model_linlin, 'Lin-Log': model_linlog}
best_y = max(y_models.items(), key=lambda x: x[1].rsquared_adj)
log_result(f"\n  Y bağımlı modeller arasında en iyi: {best_y[0]} (Adj.R²={best_y[1].rsquared_adj:.6f})")

# lnY bağımlı modeller
lny_models = {'Log-Log': model_loglog, 'Log-Lin': model_loglin}
best_lny = max(lny_models.items(), key=lambda x: x[1].rsquared_adj)
log_result(f"  lnY bağımlı modeller arasında en iyi: {best_lny[0]} (Adj.R²={best_lny[1].rsquared_adj:.6f})")

# Fonksiyonel form grafikleri
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
model_names_list = list(model_results.keys())
for idx, (name, model) in enumerate(model_results.items()):
    ax = axes[idx // 2, idx % 2]
    fitted = model.fittedvalues
    actual = model.model.endog
    ax.scatter(fitted, actual, alpha=0.5, s=20, color='steelblue')
    mn = min(fitted.min(), actual.min())
    mx = max(fitted.max(), actual.max())
    ax.plot([mn, mx], [mn, mx], 'r--', linewidth=1.5, label='45° çizgisi')
    ax.set_title(f'{name} Modeli (R²={model.rsquared:.4f})', fontsize=12, fontweight='bold')
    ax.set_xlabel('Tahmin Değerleri')
    ax.set_ylabel('Gerçek Değerler')
    ax.legend()
plt.suptitle('Fonksiyonel Form Karşılaştırması - Gerçek vs Tahmin', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/fonksiyonel_form_karsilastirma.png', dpi=150, bbox_inches='tight')
plt.close()
log_result(f"\n  ✓ Fonksiyonel form karşılaştırma grafiği kaydedildi.")

# ============================================================
# 4. ANA MODEL SEÇİMİ VE DETAYLI SONUÇLAR
# ============================================================
separator("4. ANA MODEL - LIN-LIN REGRESYON SONUÇLARI")

# Ana model olarak Lin-Lin kullanıyoruz (yorumlamada en kolay + proje gereklilikleri)
main_model = model_linlin
log_result(f"\n{main_model.summary()}")

# ============================================================
# 5. t ve F TESTLERİ
# ============================================================
separator("5. t TESTİ VE F TESTİ")

log_result("\n--- t Testi (Bireysel Katsayı Anlamlılığı) ---")
log_result(f"  Anlamlılık Düzeyi: α = {ALPHA}")

param_names_map = {
    'const': 'Sabit Terim (β₀)',
    'usd': 'USD Dolar (β₁)',
    'sanayi': 'Sanayi Üretim End. (β₂)',
    'm3': 'M3 Para Piy. (β₃)',
    'tuketici_guven': 'Tüketici Güven End. (β₄)'
}

log_result(f"\n{'Değişken':<28} {'Katsayı':<14} {'Std.Hata':<12} {'t-ist.':<10} {'p-değeri':<12} {'Karar':<10}")
log_result("-" * 90)

for param in main_model.params.index:
    coef = main_model.params[param]
    se = main_model.bse[param]
    t_val = main_model.tvalues[param]
    p_val = main_model.pvalues[param]
    label = param_names_map.get(param, param)
    decision = "RED" if p_val < ALPHA else "REDDEDİLEMEZ"

    log_result(f"  {label:<26} {coef:<14.6f} {se:<12.6f} {t_val:<10.4f} {p_val:<12.6f} {decision}")

    if param != 'const':
        log_result(f"    H₀: β = 0 ({param} TÜFE üzerinde etkisizdir)")
        log_result(f"    H₁: β ≠ 0 ({param} TÜFE üzerinde etkilidir)")
        if p_val < ALPHA:
            log_result(f"    → p={p_val:.6f} < α={ALPHA} olduğundan H₀ REDDEDİLİR.")
            log_result(f"    → {label} %{(1-ALPHA)*100:.0f} güven düzeyinde istatistiksel olarak ANLAMLIDIR.")
        else:
            log_result(f"    → p={p_val:.6f} > α={ALPHA} olduğundan H₀ REDDEDİLEMEZ.")
            log_result(f"    → {label} %{(1-ALPHA)*100:.0f} güven düzeyinde istatistiksel olarak ANLAMSIZDIR.")
        log_result("")

log_result("\n--- F Testi (Modelin Genel Anlamlılığı) ---")
log_result(f"  H₀: β₁ = β₂ = β₃ = β₄ = 0 (Model anlamsızdır, hiçbir bağımsız değişken etkili değildir)")
log_result(f"  H₁: En az bir βᵢ ≠ 0 (Model anlamlıdır)")
log_result(f"\n  F-istatistiği = {main_model.fvalue:.4f}")
log_result(f"  p-değeri = {main_model.f_pvalue:.10f}")
log_result(f"  Serbestlik Dereceleri: df1={int(main_model.df_model)}, df2={int(main_model.df_resid)}")
f_critical = stats.f.ppf(1 - ALPHA, int(main_model.df_model), int(main_model.df_resid))
log_result(f"  F-kritik (α={ALPHA}) = {f_critical:.4f}")

if main_model.f_pvalue < ALPHA:
    log_result(f"\n  → F-ist ({main_model.fvalue:.4f}) > F-kritik ({f_critical:.4f}) olduğundan H₀ REDDEDİLİR.")
    log_result(f"  → Model %{(1-ALPHA)*100:.0f} güven düzeyinde BÜTÜN OLARAK ANLAMLIDIR.")
else:
    log_result(f"\n  → F-ist ({main_model.fvalue:.4f}) < F-kritik ({f_critical:.4f}) olduğundan H₀ REDDEDİLEMEZ.")
    log_result(f"  → Model %{(1-ALPHA)*100:.0f} güven düzeyinde ANLAMSIZDIR.")

# ============================================================
# 6. MWD TESTİ (MacKinnon, White, Davidson)
# ============================================================
separator("6. MacKinnon-White-Davidson (MWD) TESTİ")

log_result("\n  Amaç: Doğrusal (Lin-Lin) ve logaritmik (Log-Log) fonksiyonel formlar arasında seçim yapmak.")

# Adım 1: Lin-Lin modelini tahmin et → Ŷ
Y_hat_linlin = model_linlin.fittedvalues

# Adım 2: Log-Log modelini tahmin et → lnŶ
lnY_hat_loglog = model_loglog.fittedvalues

# Adım 3: Z1 = ln(Ŷ_linlin) - lnŶ_loglog
Z1 = np.log(Y_hat_linlin) - lnY_hat_loglog

# Adım 4: Z2 = exp(lnŶ_loglog) - Ŷ_linlin  (alternatif: antilog)
Z2 = np.exp(lnY_hat_loglog) - Y_hat_linlin

# Test 1: Log-Log modeline Z1 eklenerek test
log_result("\n--- MWD Testi - Adım 1: Doğrusal Model Testi ---")
log_result("  H₀: Doğrusal (Lin-Lin) model doğru fonksiyonel formdur")
log_result("  H₁: Logaritmik (Log-Log) model doğru fonksiyonel formdur")

X_mwd1 = sm.add_constant(pd.DataFrame({
    'usd': lnX['usd'], 'sanayi': lnX['sanayi'],
    'm3': lnX['m3'], 'tuketici_guven': lnX['tuketici_guven'],
    'Z1': Z1
}))
model_mwd1 = sm.OLS(lnY, X_mwd1).fit()
z1_tval = model_mwd1.tvalues['Z1']
z1_pval = model_mwd1.pvalues['Z1']

log_result(f"\n  Z1 katsayısı = {model_mwd1.params['Z1']:.6f}")
log_result(f"  Z1 t-istatistiği = {z1_tval:.4f}")
log_result(f"  Z1 p-değeri = {z1_pval:.6f}")

if z1_pval < ALPHA:
    log_result(f"\n  → Z1 anlamlıdır (p={z1_pval:.6f} < {ALPHA}). H₀ REDDEDİLİR.")
    log_result(f"  → Doğrusal model reddedilir, Logaritmik model tercih edilmelidir.")
    mwd_result_1 = "Doğrusal model REDDEDİLDİ"
else:
    log_result(f"\n  → Z1 anlamsızdır (p={z1_pval:.6f} > {ALPHA}). H₀ REDDEDİLEMEZ.")
    log_result(f"  → Doğrusal model reddedilemez.")
    mwd_result_1 = "Doğrusal model REDDEDİLEMEDİ"

# Test 2: Lin-Lin modeline Z2 eklenerek test
log_result("\n--- MWD Testi - Adım 2: Logaritmik Model Testi ---")
log_result("  H₀: Logaritmik (Log-Log) model doğru fonksiyonel formdur")
log_result("  H₁: Doğrusal (Lin-Lin) model doğru fonksiyonel formdur")

X_mwd2 = sm.add_constant(pd.DataFrame({
    'usd': X_vars['usd'], 'sanayi': X_vars['sanayi'],
    'm3': X_vars['m3'], 'tuketici_guven': X_vars['tuketici_guven'],
    'Z2': Z2
}))
model_mwd2 = sm.OLS(Y, X_mwd2).fit()
z2_tval = model_mwd2.tvalues['Z2']
z2_pval = model_mwd2.pvalues['Z2']

log_result(f"\n  Z2 katsayısı = {model_mwd2.params['Z2']:.6f}")
log_result(f"  Z2 t-istatistiği = {z2_tval:.4f}")
log_result(f"  Z2 p-değeri = {z2_pval:.6f}")

if z2_pval < ALPHA:
    log_result(f"\n  → Z2 anlamlıdır (p={z2_pval:.6f} < {ALPHA}). H₀ REDDEDİLİR.")
    log_result(f"  → Logaritmik model reddedilir, Doğrusal model tercih edilmelidir.")
    mwd_result_2 = "Logaritmik model REDDEDİLDİ"
else:
    log_result(f"\n  → Z2 anlamsızdır (p={z2_pval:.6f} > {ALPHA}). H₀ REDDEDİLEMEZ.")
    log_result(f"  → Logaritmik model reddedilemez.")
    mwd_result_2 = "Logaritmik model REDDEDİLEMEDİ"

log_result(f"\n--- MWD Testi Sonuç ---")
log_result(f"  Test 1 (Doğrusal model H₀): {mwd_result_1}")
log_result(f"  Test 2 (Logaritmik model H₀): {mwd_result_2}")

# ============================================================
# 7. ÇOKLU DOĞRUSAL BAĞLANTI ANALİZİ (MULTİCOLLİNEARİTY)
# ============================================================
separator("7. ÇOKLU DOĞRUSAL BAĞLANTI ANALİZİ (MULTICOLLINEARITY)")

log_result("\n--- VIF (Variance Inflation Factor) Analizi ---")
log_result("  Kural: VIF > 10 → ciddi çoklu doğrusal bağlantı")
log_result("         VIF > 5  → orta düzeyde çoklu doğrusal bağlantı")
log_result("         VIF < 5  → sorun yok\n")

X_vif = sm.add_constant(X_vars)
vif_data = pd.DataFrame()
vif_data['Değişken'] = X_vif.columns
vif_data['VIF'] = [variance_inflation_factor(X_vif.values, i) for i in range(X_vif.shape[1])]

log_result(f"{'Değişken':<25} {'VIF':<12} {'Durum':<20}")
log_result("-" * 57)
for _, row in vif_data.iterrows():
    if row['Değişken'] == 'const':
        continue
    vif_val = row['VIF']
    label = param_names_map.get(row['Değişken'], row['Değişken'])
    if vif_val > 10:
        status = "⚠ CİDDİ SORUN"
    elif vif_val > 5:
        status = "⚡ ORTA DÜZEY"
    else:
        status = "✓ SORUN YOK"
    log_result(f"  {label:<23} {vif_val:<12.4f} {status}")

# Condition Number
cond_number = np.linalg.cond(X_linlin.values)
log_result(f"\n--- Condition Number ---")
log_result(f"  Condition Number = {cond_number:.4f}")
if cond_number > 30:
    log_result(f"  → Condition Number > 30: Çoklu doğrusal bağlantı sorunu mevcut olabilir.")
else:
    log_result(f"  → Condition Number < 30: Ciddi çoklu doğrusal bağlantı sorunu görülmemektedir.")

# Bağımsız değişkenler arası korelasyon
log_result(f"\n--- Bağımsız Değişkenler Arası Korelasyon ---")
indep_corr = X_vars.corr()
log_result(f"\n{indep_corr.round(4).to_string()}")

has_high_corr = False
for i in range(len(indep_corr.columns)):
    for j in range(i+1, len(indep_corr.columns)):
        c = indep_corr.iloc[i, j]
        if abs(c) > 0.8:
            has_high_corr = True
            log_result(f"\n  ⚠ Yüksek korelasyon: {indep_corr.columns[i]} - {indep_corr.columns[j]}: r = {c:.4f}")

if not has_high_corr:
    log_result(f"\n  ✓ Bağımsız değişkenler arasında aşırı yüksek korelasyon (|r| > 0.8) bulunmamaktadır.")

log_result(f"\n--- Çoklu Doğrusal Bağlantı Yorum ---")
max_vif = vif_data[vif_data['Değişken'] != 'const']['VIF'].max()
if max_vif > 10:
    log_result(f"  Sonuç: Ciddi çoklu doğrusal bağlantı sorunu tespit edilmiştir.")
    log_result(f"  Çözüm Önerileri:")
    log_result(f"    1. Yüksek VIF'e sahip değişkenlerden birinin modelden çıkarılması")
    log_result(f"    2. Ridge regresyon gibi düzenlileştirme yöntemlerinin kullanılması")
    log_result(f"    3. Temel bileşenler analizi (PCA) uygulanması")
elif max_vif > 5:
    log_result(f"  Sonuç: Orta düzeyde çoklu doğrusal bağlantı tespit edilmiştir.")
    log_result(f"  Bu düzey kabul edilebilir sınırlarda olup, dikkatli yorumlanmalıdır.")
else:
    log_result(f"  Sonuç: Ciddi bir çoklu doğrusal bağlantı sorunu bulunmamaktadır.")

# ============================================================
# 8. DURAĞANLIK / BİRİM KÖK TESTİ (ADF)
# ============================================================
separator("8. DURAĞANLIK - AUGMENTED DICKEY-FULLER (ADF) TESTİ")

log_result(f"\n  H₀: Seri birim kök içerir (durağan DEĞİLDİR)")
log_result(f"  H₁: Seri birim kök içermez (DURAĞANDIR)")
log_result(f"  Anlamlılık Düzeyi: α = {ALPHA}\n")

adf_results = {}
log_result(f"{'Değişken':<25} {'ADF İst.':<12} {'p-değeri':<12} {'Gecikme':<10} {'Karar':<20}")
log_result("-" * 80)

for var in data.columns:
    adf_result = adfuller(data[var], autolag='AIC')
    adf_stat = adf_result[0]
    adf_pval = adf_result[1]
    adf_lags = adf_result[2]
    adf_crit = adf_result[4]

    label = var_labels[var]
    decision = "DURAĞAN" if adf_pval < ALPHA else "DURAĞAN DEĞİL"
    adf_results[var] = {'stat': adf_stat, 'pval': adf_pval, 'lags': adf_lags, 'critical': adf_crit, 'decision': decision}

    log_result(f"  {label:<23} {adf_stat:<12.4f} {adf_pval:<12.6f} {adf_lags:<10} {decision}")

# Detaylı yorumlar
log_result(f"\n--- Detaylı ADF Testi Sonuçları ---")
for var in data.columns:
    r = adf_results[var]
    label = var_labels[var]
    log_result(f"\n  {label}:")
    log_result(f"    ADF İstatistiği: {r['stat']:.4f}")
    log_result(f"    p-değeri: {r['pval']:.6f}")
    log_result(f"    Kritik Değerler: 1%: {r['critical']['1%']:.4f}, 5%: {r['critical']['5%']:.4f}, 10%: {r['critical']['10%']:.4f}")
    if r['pval'] < ALPHA:
        log_result(f"    → p={r['pval']:.6f} < α={ALPHA}, H₀ REDDEDİLİR. Seri DURAĞANDIR.")
    else:
        log_result(f"    → p={r['pval']:.6f} > α={ALPHA}, H₀ REDDEDİLEMEZ. Seri DURAĞAN DEĞİLDİR.")

# Durağan olmayan seriler için birinci fark testi
non_stationary = [var for var, r in adf_results.items() if r['decision'] == 'DURAĞAN DEĞİL']
if non_stationary:
    log_result(f"\n--- Birinci Fark ile Durağanlık Kontrolü ---")
    log_result(f"  Durağan olmayan seriler için birinci fark (Δ) alınıyor...\n")

    log_result(f"{'Değişken (Δ)':<25} {'ADF İst.':<12} {'p-değeri':<12} {'Karar':<20}")
    log_result("-" * 70)

    for var in non_stationary:
        diff_series = data[var].diff().dropna()
        adf_diff = adfuller(diff_series, autolag='AIC')
        label = f"Δ{var_labels[var]}"
        decision = "DURAĞAN" if adf_diff[1] < ALPHA else "DURAĞAN DEĞİL"
        log_result(f"  {label:<23} {adf_diff[0]:<12.4f} {adf_diff[1]:<12.6f} {decision}")

# ============================================================
# 9. WALD TESTİ
# ============================================================
separator("9. WALD TESTİ")

log_result("\n  Amaç: Bağımsız değişkenlerin alt gruplarının birlikte anlamlılığını test etmek.")

# Test 1: Tüm döviz ve parasal değişkenlerin birlikte anlamlılığı
log_result("\n--- Wald Testi 1: Parasal Değişkenler ---")
log_result("  H₀: β₁ (USD) = β₃ (M3) = 0 (Parasal değişkenler birlikte anlamsızdır)")
log_result("  H₁: En az bir βᵢ ≠ 0 (En az biri anlamlıdır)")

# Kısıtlama: usd=0, m3=0
r_matrix_1 = np.zeros((2, len(main_model.params)))
r_matrix_1[0, list(main_model.params.index).index('usd')] = 1
r_matrix_1[1, list(main_model.params.index).index('m3')] = 1

wald_test_1 = main_model.wald_test(r_matrix_1)
wald_f1 = float(wald_test_1.fvalue)
wald_p1 = float(wald_test_1.pvalue)

log_result(f"\n  Wald F-istatistiği = {wald_f1:.4f}")
log_result(f"  p-değeri = {wald_p1:.6f}")

if wald_p1 < ALPHA:
    log_result(f"  → p={wald_p1:.6f} < α={ALPHA}, H₀ REDDEDİLİR.")
    log_result(f"  → Parasal değişkenler (USD, M3) birlikte İSTATİSTİKSEL OLARAK ANLAMLIDIR.")
else:
    log_result(f"  → p={wald_p1:.6f} > α={ALPHA}, H₀ REDDEDİLEMEZ.")
    log_result(f"  → Parasal değişkenler birlikte anlamsızdır.")

# Test 2: Reel ekonomi değişkenleri
log_result("\n--- Wald Testi 2: Reel Ekonomi Değişkenleri ---")
log_result("  H₀: β₂ (Sanayi) = β₄ (TüketiciGüven) = 0 (Reel ekonomi değişkenleri birlikte anlamsızdır)")
log_result("  H₁: En az bir βᵢ ≠ 0")

r_matrix_2 = np.zeros((2, len(main_model.params)))
r_matrix_2[0, list(main_model.params.index).index('sanayi')] = 1
r_matrix_2[1, list(main_model.params.index).index('tuketici_guven')] = 1

wald_test_2 = main_model.wald_test(r_matrix_2)
wald_f2 = float(wald_test_2.fvalue)
wald_p2 = float(wald_test_2.pvalue)

log_result(f"\n  Wald F-istatistiği = {wald_f2:.4f}")
log_result(f"  p-değeri = {wald_p2:.6f}")

if wald_p2 < ALPHA:
    log_result(f"  → p={wald_p2:.6f} < α={ALPHA}, H₀ REDDEDİLİR.")
    log_result(f"  → Reel ekonomi değişkenleri (Sanayi, Tüketici Güven) birlikte ANLAMLIDIR.")
else:
    log_result(f"  → p={wald_p2:.6f} > α={ALPHA}, H₀ REDDEDİLEMEZ.")
    log_result(f"  → Reel ekonomi değişkenleri birlikte anlamsızdır.")

# Test 3: Tüm bağımsız değişkenlerin birlikte sıfır olması (F testine eşdeğer)
log_result("\n--- Wald Testi 3: Tüm Bağımsız Değişkenler ---")
log_result("  H₀: β₁ = β₂ = β₃ = β₄ = 0 (Tüm bağımsız değişkenler birlikte anlamsızdır)")
log_result("  H₁: En az bir βᵢ ≠ 0")

r_matrix_3 = np.zeros((4, len(main_model.params)))
for idx_w, var_w in enumerate(['usd', 'sanayi', 'm3', 'tuketici_guven']):
    r_matrix_3[idx_w, list(main_model.params.index).index(var_w)] = 1

wald_test_3 = main_model.wald_test(r_matrix_3)
wald_f3 = float(wald_test_3.fvalue)
wald_p3 = float(wald_test_3.pvalue)

log_result(f"\n  Wald F-istatistiği = {wald_f3:.4f}")
log_result(f"  p-değeri = {wald_p3:.10f}")

if wald_p3 < ALPHA:
    log_result(f"  → p < α={ALPHA}, H₀ REDDEDİLİR.")
    log_result(f"  → Tüm bağımsız değişkenler birlikte İSTATİSTİKSEL OLARAK ANLAMLIDIR.")
else:
    log_result(f"  → p > α={ALPHA}, H₀ REDDEDİLEMEZ.")

# ============================================================
# 10. CHOW TESTİ (YAPISAL KIRILMA)
# ============================================================
separator("10. CHOW TESTİ (YAPISAL KIRILMA)")

# Kırılma noktası: 2018-08 (Türk Lirası krizi)
break_point = '2018-08'
log_result(f"\n  Kırılma Noktası: {break_point} (Ağustos 2018 - Türk Lirası Krizi)")
log_result(f"\n  H₀: İki dönem arasında yapısal kırılma YOKTUR (parametreler stabildir)")
log_result(f"  H₁: İki dönem arasında yapısal kırılma VARDIR (parametreler değişmiştir)")

# Veriyi ikiye böl
data_1 = data[data.index < break_point]
data_2 = data[data.index >= break_point]

log_result(f"\n  Dönem 1: {data_1.index[0].strftime('%Y-%m')} - {data_1.index[-1].strftime('%Y-%m')} (n₁={len(data_1)})")
log_result(f"  Dönem 2: {data_2.index[0].strftime('%Y-%m')} - {data_2.index[-1].strftime('%Y-%m')} (n₂={len(data_2)})")

# Tüm dönem regresyonu
X_full = sm.add_constant(data[['usd', 'sanayi', 'm3', 'tuketici_guven']])
model_full = sm.OLS(data['tufe'], X_full).fit()
RSS_full = model_full.ssr

# Dönem 1 regresyonu
X_1 = sm.add_constant(data_1[['usd', 'sanayi', 'm3', 'tuketici_guven']])
model_1 = sm.OLS(data_1['tufe'], X_1).fit()
RSS_1 = model_1.ssr

# Dönem 2 regresyonu
X_2 = sm.add_constant(data_2[['usd', 'sanayi', 'm3', 'tuketici_guven']])
model_2 = sm.OLS(data_2['tufe'], X_2).fit()
RSS_2 = model_2.ssr

n = len(data)
k = len(main_model.params)  # parametre sayısı (sabit dahil)
n1 = len(data_1)
n2 = len(data_2)

# Chow F istatistiği
chow_f = ((RSS_full - (RSS_1 + RSS_2)) / k) / ((RSS_1 + RSS_2) / (n - 2 * k))
chow_p = 1 - stats.f.cdf(chow_f, k, n - 2 * k)
chow_f_critical = stats.f.ppf(1 - ALPHA, k, n - 2 * k)

log_result(f"\n  RSS (Tam Dönem) = {RSS_full:.4f}")
log_result(f"  RSS (Dönem 1) = {RSS_1:.4f}")
log_result(f"  RSS (Dönem 2) = {RSS_2:.4f}")
log_result(f"\n  Chow F-istatistiği = {chow_f:.4f}")
log_result(f"  F-kritik (α={ALPHA}, df1={k}, df2={n-2*k}) = {chow_f_critical:.4f}")
log_result(f"  p-değeri = {chow_p:.6f}")

if chow_f > chow_f_critical:
    log_result(f"\n  → Chow F ({chow_f:.4f}) > F-kritik ({chow_f_critical:.4f}), H₀ REDDEDİLİR.")
    log_result(f"  → {break_point} tarihinde YAPISAL KIRILMA TESPİT EDİLMİŞTİR.")
    log_result(f"  → 2018 TL krizi, enflasyon modelinin parametrelerini önemli ölçüde değiştirmiştir.")
else:
    log_result(f"\n  → Chow F ({chow_f:.4f}) < F-kritik ({chow_f_critical:.4f}), H₀ REDDEDİLEMEZ.")
    log_result(f"  → {break_point} tarihinde yapısal kırılma tespit edilememiştir.")

# Chow testi - COVID kırılması
break_point_2 = '2020-03'
log_result(f"\n--- Chow Testi - COVID-19 Kırılması ---")
log_result(f"  Kırılma Noktası: {break_point_2} (Mart 2020 - COVID-19 Pandemisi)")

data_c1 = data[data.index < break_point_2]
data_c2 = data[data.index >= break_point_2]

log_result(f"  Dönem 1: {data_c1.index[0].strftime('%Y-%m')} - {data_c1.index[-1].strftime('%Y-%m')} (n₁={len(data_c1)})")
log_result(f"  Dönem 2: {data_c2.index[0].strftime('%Y-%m')} - {data_c2.index[-1].strftime('%Y-%m')} (n₂={len(data_c2)})")

X_c1 = sm.add_constant(data_c1[['usd', 'sanayi', 'm3', 'tuketici_guven']])
model_c1 = sm.OLS(data_c1['tufe'], X_c1).fit()
RSS_c1 = model_c1.ssr

X_c2 = sm.add_constant(data_c2[['usd', 'sanayi', 'm3', 'tuketici_guven']])
model_c2 = sm.OLS(data_c2['tufe'], X_c2).fit()
RSS_c2 = model_c2.ssr

chow_f2 = ((RSS_full - (RSS_c1 + RSS_c2)) / k) / ((RSS_c1 + RSS_c2) / (n - 2 * k))
chow_p2 = 1 - stats.f.cdf(chow_f2, k, n - 2 * k)

log_result(f"\n  Chow F-istatistiği = {chow_f2:.4f}")
log_result(f"  p-değeri = {chow_p2:.6f}")

if chow_f2 > chow_f_critical:
    log_result(f"  → Chow F ({chow_f2:.4f}) > F-kritik ({chow_f_critical:.4f}), H₀ REDDEDİLİR.")
    log_result(f"  → COVID-19 döneminde YAPISAL KIRILMA TESPİT EDİLMİŞTİR.")
else:
    log_result(f"  → Chow F ({chow_f2:.4f}) < F-kritik ({chow_f_critical:.4f}), H₀ REDDEDİLEMEZ.")
    log_result(f"  → COVID-19 döneminde yapısal kırılma tespit edilememiştir.")

# ============================================================
# 11. PARK TESTİ (DEĞİŞEN VARYANS)
# ============================================================
separator("11. PARK TESTİ (DEĞİŞEN VARYANS / HETEROSCEDASTICITY)")

log_result(f"\n  H₀: Sabit varyans vardır (Homoscedasticity)")
log_result(f"  H₁: Değişen varyans vardır (Heteroscedasticity)")
log_result(f"\n  Yöntem: ln(eᵢ²) = α + β·ln(Xⱼ) + vᵢ regresyonunda β'nın anlamlılığı test edilir.")

residuals = main_model.resid
ln_e2 = np.log(residuals**2)

park_results = {}
log_result(f"\n{'Değişken':<25} {'β katsayısı':<14} {'t-ist.':<10} {'p-değeri':<12} {'Karar':<20}")
log_result("-" * 80)

for var in ['usd', 'sanayi', 'm3', 'tuketici_guven']:
    ln_x = np.log(data[var])
    X_park = sm.add_constant(ln_x)
    model_park = sm.OLS(ln_e2, X_park).fit()
    park_coef = model_park.params.iloc[1]
    park_t = model_park.tvalues.iloc[1]
    park_p = model_park.pvalues.iloc[1]
    decision = "DEĞİŞEN VARYANS" if park_p < ALPHA else "SABİT VARYANS"
    park_results[var] = {'coef': park_coef, 't': park_t, 'p': park_p, 'decision': decision}
    label = param_names_map.get(var, var)
    log_result(f"  {label:<23} {park_coef:<14.6f} {park_t:<10.4f} {park_p:<12.6f} {decision}")

log_result(f"\n--- Park Testi Yorum ---")
het_count = sum(1 for r in park_results.values() if r['decision'] == 'DEĞİŞEN VARYANS')
if het_count > 0:
    log_result(f"  {het_count} değişken için değişen varyans (heteroscedasticity) tespit edilmiştir.")
    for var, r in park_results.items():
        if r['decision'] == 'DEĞİŞEN VARYANS':
            label = param_names_map.get(var, var)
            log_result(f"    → {label}: β={r['coef']:.4f}, p={r['p']:.6f} < {ALPHA}")
    log_result(f"  Bu durum OLS tahminlerinin etkin olmadığına işaret etmektedir.")
    log_result(f"  Çözüm: Ağırlıklı En Küçük Kareler (WLS) veya Robust standart hatalar kullanılabilir.")
else:
    log_result(f"  Hiçbir değişken için değişen varyans sorunu tespit edilmemiştir.")

# ============================================================
# 12. GOLDFELD-QUANDT TESTİ
# ============================================================
separator("12. GOLDFELD-QUANDT TESTİ (DEĞİŞEN VARYANS)")

log_result(f"\n  H₀: σ₁² = σ₂² (Varyanslar eşittir - Sabit varyans / Homoscedasticity)")
log_result(f"  H₁: σ₁² ≠ σ₂² (Varyanslar eşit değildir - Değişen varyans / Heteroscedasticity)")
log_result(f"\n  Yöntem: Veri, şüpheli değişkene göre sıralanır, ortadaki gözlemler çıkarılır,")
log_result(f"          iki alt grubun kalıntı varyansları karşılaştırılır.")

gq_results = {}
log_result(f"\n{'Sıralama Değişkeni':<25} {'F-ist.':<12} {'p-değeri':<12} {'Karar':<25}")
log_result("-" * 75)

for var in ['usd', 'sanayi', 'm3', 'tuketici_guven']:
    # Veriyi sırala
    sorted_idx = data[var].argsort()
    Y_sorted = Y.iloc[sorted_idx].values
    X_sorted = X_linlin.iloc[sorted_idx].values

    try:
        gq_stat, gq_p, ordering = het_goldfeldquandt(Y_sorted, X_sorted, alternative='two-sided')
        label = param_names_map.get(var, var)
        decision = "DEĞİŞEN VARYANS" if gq_p < ALPHA else "SABİT VARYANS"
        gq_results[var] = {'stat': gq_stat, 'p': gq_p, 'decision': decision}
        log_result(f"  {label:<23} {gq_stat:<12.4f} {gq_p:<12.6f} {decision}")
    except Exception as e:
        log_result(f"  {param_names_map.get(var, var):<23} Hesaplanamadı: {str(e)[:40]}")

log_result(f"\n--- Goldfeld-Quandt Testi Yorum ---")
gq_het_count = sum(1 for r in gq_results.values() if r['decision'] == 'DEĞİŞEN VARYANS')
if gq_het_count > 0:
    log_result(f"  {gq_het_count} değişken için değişen varyans tespit edilmiştir.")
    for var, r in gq_results.items():
        if r['decision'] == 'DEĞİŞEN VARYANS':
            log_result(f"    → {param_names_map.get(var, var)}: F={r['stat']:.4f}, p={r['p']:.6f}")
else:
    log_result(f"  Goldfeld-Quandt testine göre değişen varyans sorunu tespit edilmemiştir.")

# ============================================================
# 13. WHITE TESTİ (HETEROSCEDASTICITY)
# ============================================================
separator("13. WHITE TESTİ (DEĞİŞEN VARYANS)")

log_result(f"\n  H₀: Sabit varyans vardır (Homoscedasticity)")
log_result(f"  H₁: Değişen varyans vardır (Heteroscedasticity)")
log_result(f"\n  Yöntem: eᵢ² = α₀ + α₁X₁ + α₂X₂ + ... + α·X₁² + α·X₂² + ... + α·X₁X₂ + ...")

white_test = het_white(main_model.resid, main_model.model.exog)
white_lm = white_test[0]
white_lm_p = white_test[1]
white_f = white_test[2]
white_f_p = white_test[3]

log_result(f"\n  White LM İstatistiği = {white_lm:.4f}")
log_result(f"  LM p-değeri = {white_lm_p:.6f}")
log_result(f"  White F İstatistiği = {white_f:.4f}")
log_result(f"  F p-değeri = {white_f_p:.6f}")

if white_lm_p < ALPHA:
    log_result(f"\n  → LM p-değeri ({white_lm_p:.6f}) < α={ALPHA}, H₀ REDDEDİLİR.")
    log_result(f"  → White testine göre DEĞİŞEN VARYANS sorunu VARDIR.")
    log_result(f"  → OLS tahminleri hala tutarsız değildir ancak ETKİN DEĞİLDİR.")
    log_result(f"  → Standart hatalar güvenilir değildir, t ve F testleri yanıltıcı olabilir.")
    log_result(f"  → Çözüm: HAC (Heteroscedasticity-Autocorrelation Consistent) standart hatalar kullanılabilir.")
else:
    log_result(f"\n  → LM p-değeri ({white_lm_p:.6f}) > α={ALPHA}, H₀ REDDEDİLEMEZ.")
    log_result(f"  → White testine göre sabit varyans varsayımı geçerlidir.")

# ============================================================
# 14. DURBIN-WATSON TESTİ VE DURBIN h TESTİ
# ============================================================
separator("14. DURBIN-WATSON TESTİ VE DURBIN-WATSON h TESTİ")

# Durbin-Watson Testi
log_result("\n--- Durbin-Watson (DW) Testi ---")
log_result(f"  H₀: Birinci dereceden otokorelasyon YOKTUR (ρ = 0)")
log_result(f"  H₁: Birinci dereceden otokorelasyon VARDIR (ρ ≠ 0)")

dw_stat = durbin_watson(main_model.resid)
log_result(f"\n  DW İstatistiği = {dw_stat:.4f}")

# DW kritik değerler (n=100, k=4 bağımsız değişken, α=0.05 için yaklaşık değerler)
# Durbin-Watson tablolarından
n_obs = len(data)
k_vars = 4  # bağımsız değişken sayısı
log_result(f"  n = {n_obs}, k = {k_vars}")

# Yaklaşık kritik değerler (n=100, k=4, α=0.05)
dL = 1.592
dU = 1.758

log_result(f"\n  Kritik Değerler (α={ALPHA}, n={n_obs}, k={k_vars}):")
log_result(f"    dL = {dL:.3f}")
log_result(f"    dU = {dU:.3f}")
log_result(f"    4-dU = {4-dU:.3f}")
log_result(f"    4-dL = {4-dL:.3f}")

log_result(f"\n  Karar Kuralları:")
log_result(f"    0 < DW < dL ({dL:.3f}): Pozitif otokorelasyon VAR")
log_result(f"    dL < DW < dU ({dL:.3f}-{dU:.3f}): Kararsız bölge")
log_result(f"    dU < DW < 4-dU ({dU:.3f}-{4-dU:.3f}): Otokorelasyon YOK")
log_result(f"    4-dU < DW < 4-dL ({4-dU:.3f}-{4-dL:.3f}): Kararsız bölge")
log_result(f"    4-dL < DW < 4 ({4-dL:.3f}-4): Negatif otokorelasyon VAR")

if dw_stat < dL:
    dw_decision = "POZİTİF OTOKORELASYON VARDIR"
    log_result(f"\n  → DW = {dw_stat:.4f} < dL = {dL:.3f}")
    log_result(f"  → {dw_decision}")
    log_result(f"  → H₀ REDDEDİLİR. Modelde pozitif otokorelasyon sorunu mevcuttur.")
elif dw_stat < dU:
    dw_decision = "KARARSIZ BÖLGE"
    log_result(f"\n  → dL ({dL:.3f}) < DW ({dw_stat:.4f}) < dU ({dU:.3f})")
    log_result(f"  → {dw_decision}. Kesin bir karar verilemez.")
elif dw_stat < 4 - dU:
    dw_decision = "OTOKORELASYON YOKTUR"
    log_result(f"\n  → dU ({dU:.3f}) < DW ({dw_stat:.4f}) < 4-dU ({4-dU:.3f})")
    log_result(f"  → {dw_decision}")
    log_result(f"  → H₀ REDDEDİLEMEZ. Otokorelasyon sorunu tespit edilmemiştir.")
elif dw_stat < 4 - dL:
    dw_decision = "KARARSIZ BÖLGE (NEGATİF)"
    log_result(f"\n  → 4-dU ({4-dU:.3f}) < DW ({dw_stat:.4f}) < 4-dL ({4-dL:.3f})")
    log_result(f"  → {dw_decision}. Kesin bir karar verilemez.")
else:
    dw_decision = "NEGATİF OTOKORELASYON VARDIR"
    log_result(f"\n  → DW = {dw_stat:.4f} > 4-dL = {4-dL:.3f}")
    log_result(f"  → {dw_decision}")
    log_result(f"  → H₀ REDDEDİLİR. Modelde negatif otokorelasyon sorunu mevcuttur.")

# Durbin h Testi
log_result("\n\n--- Durbin h Testi ---")
log_result(f"  Amaç: Gecikmeli bağımlı değişken içeren modellerde otokorelasyonun test edilmesi")
log_result(f"  H₀: Otokorelasyon YOKTUR")
log_result(f"  H₁: Otokorelasyon VARDIR")

# Gecikmeli model tahmin et
Y_lag = data['tufe'].shift(1)
data_lag = data.copy()
data_lag['tufe_lag'] = Y_lag
data_lag = data_lag.dropna()

X_lag = sm.add_constant(data_lag[['usd', 'sanayi', 'm3', 'tuketici_guven', 'tufe_lag']])
model_lag = sm.OLS(data_lag['tufe'], X_lag).fit()

# DW hesapla gecikmeli model için
dw_lag = durbin_watson(model_lag.resid)
rho_hat = 1 - dw_lag / 2

# Gecikmeli bağımlı değişkenin varyansı
var_beta_lag = model_lag.bse['tufe_lag']**2
n_lag = len(data_lag)

log_result(f"\n  Gecikmeli Model Tahmin Sonuçları:")
log_result(f"    ρ̂ = 1 - DW/2 = 1 - {dw_lag:.4f}/2 = {rho_hat:.4f}")
log_result(f"    n = {n_lag}")
log_result(f"    Var(β̂_lag) = {var_beta_lag:.8f}")

# h = ρ̂ * sqrt(n / (1 - n*Var(β̂)))
denominator = 1 - n_lag * var_beta_lag

if denominator > 0:
    h_stat = rho_hat * np.sqrt(n_lag / denominator)
    h_p = 2 * (1 - stats.norm.cdf(abs(h_stat)))

    log_result(f"    n · Var(β̂_lag) = {n_lag * var_beta_lag:.6f}")
    log_result(f"    1 - n · Var(β̂_lag) = {denominator:.6f}")
    log_result(f"\n  h istatistiği = {h_stat:.4f}")
    log_result(f"  |h| = {abs(h_stat):.4f}")
    log_result(f"  Kritik Değer (Z₀.₀₂₅) = 1.96")

    if abs(h_stat) > 1.96:
        log_result(f"\n  → |h| = {abs(h_stat):.4f} > 1.96, H₀ REDDEDİLİR.")
        log_result(f"  → Gecikmeli modelde OTOKORELASYON VARDIR.")
    else:
        log_result(f"\n  → |h| = {abs(h_stat):.4f} < 1.96, H₀ REDDEDİLEMEZ.")
        log_result(f"  → Gecikmeli modelde otokorelasyon tespit edilmemiştir.")
else:
    log_result(f"\n  ⚠ n · Var(β̂_lag) = {n_lag * var_beta_lag:.4f} > 1")
    log_result(f"  → Durbin h testi uygulanamaz (karekök içi negatif).")
    log_result(f"  → Alternatif: Breusch-Godfrey LM testi kullanılabilir.")

    # Breusch-Godfrey alternatif
    from statsmodels.stats.diagnostic import acorr_breusch_godfrey
    bg_lm, bg_p, bg_f, bg_fp = acorr_breusch_godfrey(model_lag, nlags=1)
    log_result(f"\n  Breusch-Godfrey LM Testi (Alternatif):")
    log_result(f"    LM istatistiği = {bg_lm:.4f}")
    log_result(f"    p-değeri = {bg_p:.6f}")
    if bg_p < ALPHA:
        log_result(f"    → H₀ REDDEDİLİR. Otokorelasyon vardır.")
    else:
        log_result(f"    → H₀ REDDEDİLEMEZ. Otokorelasyon yoktur.")

# Otokorelasyon grafikleri
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Kalıntı zaman serisi
axes[0].plot(data.index, main_model.resid, color='steelblue', linewidth=1)
axes[0].axhline(y=0, color='red', linestyle='--', linewidth=1)
axes[0].set_title('Kalıntıların Zaman Serisi', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Tarih')
axes[0].set_ylabel('Kalıntı (eᵢ)')
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Kalıntı vs Gecikmeli Kalıntı
axes[1].scatter(main_model.resid.iloc[:-1], main_model.resid.iloc[1:], alpha=0.5, s=20, color='steelblue')
axes[1].axhline(y=0, color='red', linestyle='--', linewidth=0.5)
axes[1].axvline(x=0, color='red', linestyle='--', linewidth=0.5)
axes[1].set_title('eₜ vs eₜ₋₁ (Otokorelasyon Görselleştirme)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('eₜ₋₁')
axes[1].set_ylabel('eₜ')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/otokorelasyon_grafikleri.png', dpi=150, bbox_inches='tight')
plt.close()
log_result(f"\n  ✓ Otokorelasyon grafikleri kaydedildi.")

# ============================================================
# 15. EK DİAGNOSTİK GRAFİKLER
# ============================================================
separator("15. DİAGNOSTİK GRAFİKLER")

# Kalıntı analiz grafikleri
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Kalıntı vs Tahmin
axes[0, 0].scatter(main_model.fittedvalues, main_model.resid, alpha=0.5, s=20, color='steelblue')
axes[0, 0].axhline(y=0, color='red', linestyle='--', linewidth=1)
axes[0, 0].set_title('Kalıntı vs Tahmin Değerleri', fontsize=11, fontweight='bold')
axes[0, 0].set_xlabel('Tahmin (Ŷ)')
axes[0, 0].set_ylabel('Kalıntı (eᵢ)')

# 2. Normal Q-Q Plot
sm.qqplot(main_model.resid, line='45', ax=axes[0, 1], markerfacecolor='steelblue', alpha=0.5)
axes[0, 1].set_title('Normal Q-Q Grafiği', fontsize=11, fontweight='bold')

# 3. Kalıntı histogram
axes[1, 0].hist(main_model.resid, bins=20, density=True, color='steelblue', alpha=0.7, edgecolor='white')
x_norm = np.linspace(main_model.resid.min(), main_model.resid.max(), 100)
axes[1, 0].plot(x_norm, stats.norm.pdf(x_norm, main_model.resid.mean(), main_model.resid.std()),
                'r-', linewidth=2, label='Normal Dağılım')
axes[1, 0].set_title('Kalıntı Dağılımı', fontsize=11, fontweight='bold')
axes[1, 0].set_xlabel('Kalıntı')
axes[1, 0].set_ylabel('Yoğunluk')
axes[1, 0].legend()

# 4. Gerçek vs Tahmin
axes[1, 1].plot(data.index, Y, color='steelblue', linewidth=1.5, label='Gerçek TÜFE')
axes[1, 1].plot(data.index, main_model.fittedvalues, color='red', linewidth=1.5, linestyle='--', label='Tahmin TÜFE')
axes[1, 1].set_title('Gerçek vs Tahmin Değerleri', fontsize=11, fontweight='bold')
axes[1, 1].set_xlabel('Tarih')
axes[1, 1].set_ylabel('TÜFE')
axes[1, 1].legend()
axes[1, 1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

plt.suptitle('Model Diagnostik Grafikleri (Lin-Lin)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/diagnostik_grafikler.png', dpi=150, bbox_inches='tight')
plt.close()
log_result(f"  ✓ Diagnostik grafikleri kaydedildi.")

# Değişen varyans grafikleri
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
for idx, var in enumerate(['usd', 'sanayi', 'm3', 'tuketici_guven']):
    ax = axes[idx // 2, idx % 2]
    ax.scatter(data[var], main_model.resid**2, alpha=0.5, s=20, color='steelblue')
    ax.set_title(f'eᵢ² vs {param_names_map.get(var, var)}', fontsize=11, fontweight='bold')
    ax.set_xlabel(var_labels.get(var, var))
    ax.set_ylabel('eᵢ²')

plt.suptitle('Değişen Varyans Görselleştirme (eᵢ² vs Bağımsız Değişkenler)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/degisen_varyans_grafikleri.png', dpi=150, bbox_inches='tight')
plt.close()
log_result(f"  ✓ Değişen varyans grafikleri kaydedildi.")

# ============================================================
# 16. GENEL SONUÇLAR VE DEĞERLENDİRME
# ============================================================
separator("16. GENEL SONUÇLAR VE DEĞERLENDİRME")

log_result(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    IST3102 EKONOMETRİ PROJESİ - ÖZET TABLO                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Bağımlı Değişken   : TÜFE (Tüketici Fiyat Endeksi)                        ║
║ Bağımsız Değişkenler: USD, Sanayi Üretim End., M3, Tüketici Güven End.    ║
║ Dönem              : 2015:04 - 2023:07 (100 gözlem)                       ║
║ Ana Model          : Lin-Lin (Y = β₀ + β₁X₁ + β₂X₂ + β₃X₃ + β₄X₄ + ε)   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ R²                 : {main_model.rsquared:.6f}                                        ║
║ Düzeltilmiş R²     : {main_model.rsquared_adj:.6f}                                        ║
║ F-istatistiği      : {main_model.fvalue:.4f}                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

log_result(f"\n  --- Test Sonuçları Özet Tablosu ---\n")
log_result(f"{'Test':<35} {'Sonuç':<40}")
log_result("-" * 75)
log_result(f"{'F Testi (Genel Anlamlılık)':<35} {'Model ANLAMLI' if main_model.f_pvalue < ALPHA else 'Model ANLAMSIZ':<40}")

# t testi özeti
for var in ['usd', 'sanayi', 'm3', 'tuketici_guven']:
    p = main_model.pvalues[var]
    label = param_names_map.get(var, var).split('(')[0].strip()
    status = "ANLAMLI" if p < ALPHA else "ANLAMSIZ"
    log_result(f"{'t Testi - ' + label:<35} {status + f' (p={p:.4f})':<40}")

log_result(f"{'MWD Testi':<35} {mwd_result_1 + ' / ' + mwd_result_2:<40}")

# VIF durumu
max_vif_var = vif_data[vif_data['Değişken'] != 'const'].sort_values('VIF', ascending=False).iloc[0]
max_vif_val = max_vif_var['VIF']
vif_status_str = f"Max VIF={max_vif_val:.2f}" + (" ⚠ SORUN" if max_vif_val > 10 else " ✓ KABUL")
log_result(f"{'Çoklu Doğrusal Bağlantı (VIF)':<35} {vif_status_str:<40}")

# ADF durumu
non_stat_vars = [var_labels[v] for v, r in adf_results.items() if r['decision'] == 'DURAĞAN DEĞİL']
if non_stat_vars:
    log_result(f"{'ADF (Birim Kök) Testi':<35} {'DURAĞAN DEĞİL: ' + ', '.join(non_stat_vars[:2]) + ('...' if len(non_stat_vars) > 2 else ''):<40}")
else:
    log_result(f"{'ADF (Birim Kök) Testi':<35} {'Tüm seriler DURAĞAN':<40}")

log_result(f"{'Wald Testi (Parasal Değ.)':<35} {'ANLAMLI' if wald_p1 < ALPHA else 'ANLAMSIZ':<40}")
log_result(f"{'Wald Testi (Reel Ekonomi Değ.)':<35} {'ANLAMLI' if wald_p2 < ALPHA else 'ANLAMSIZ':<40}")
log_result(f"{'Chow Testi (2018 Kriz)':<35} {'YAPISAL KIRILMA VAR' if chow_f > chow_f_critical else 'Yapısal kırılma yok':<40}")
log_result(f"{'Chow Testi (COVID-19)':<35} {'YAPISAL KIRILMA VAR' if chow_f2 > chow_f_critical else 'Yapısal kırılma yok':<40}")

park_status = 'DEĞİŞEN VARYANS' if het_count > 0 else 'SABİT VARYANS'
log_result(f"{'Park Testi':<35} {park_status:<40}")

gq_status = 'DEĞİŞEN VARYANS' if gq_het_count > 0 else 'SABİT VARYANS'
log_result(f"{'Goldfeld-Quandt Testi':<35} {gq_status:<40}")

white_status = 'DEĞİŞEN VARYANS' if white_lm_p < ALPHA else 'SABİT VARYANS'
log_result(f"{'White Testi':<35} {white_status:<40}")

log_result(f"{'Durbin-Watson Testi':<35} {dw_decision:<40}")

# ============================================================
# SONUÇLARI DOSYAYA KAYDET
# ============================================================
with open('analiz_sonuclari.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results_text))

log_result(f"\n{'='*80}")
log_result(f"  TÜM ANALİZLER TAMAMLANDI!")
log_result(f"  Sonuçlar: analiz_sonuclari.txt")
log_result(f"  Grafikler: {OUTPUT_DIR}/ klasörü")
log_result(f"{'='*80}")
