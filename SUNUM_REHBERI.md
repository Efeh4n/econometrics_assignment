# 📘 IST3102 Ekonometri Proje - Kullanım ve Sunum Rehberi

> Bu doküman, proje dosyalarını nasıl kullanacağınızı, her testin ne anlama geldiğini ve sunumda nelere dikkat etmeniz gerektiğini açıklamaktadır.

---

## 📁 Proje Dosya Yapısı

```
ekonometri proje/
├── Enflasyon verileri1.xlsx     ← Ham veri (Excel) — Teslim edilecek
├── ekonometri_analiz.py         ← Python analiz scripti — Teslim edilecek
├── analiz_sonuclari.txt         ← Tüm test sonuçları (metin) — Referans
└── grafikler/                   ← Tüm grafikler — Word dosyasına eklenecek
    ├── tufe_zaman_serisi.png
    ├── usd_zaman_serisi.png
    ├── sanayi_zaman_serisi.png
    ├── m3_zaman_serisi.png
    ├── tuketici_guven_zaman_serisi.png
    ├── tum_degiskenler.png
    ├── korelasyon_matrisi.png
    ├── fonksiyonel_form_karsilastirma.png
    ├── diagnostik_grafikler.png
    ├── degisen_varyans_grafikleri.png
    └── otokorelasyon_grafikleri.png
```

---

## 🖥️ Analizi Nasıl Çalıştırırım?

### Gereksinimler
Bilgisayarınızda **Python 3** ve şu kütüphaneler kurulu olmalı:
```
pandas, numpy, matplotlib, statsmodels, scipy, openpyxl
```

Eğer kurulu değilse terminalde şunu çalıştırın:
```bash
pip install pandas numpy matplotlib statsmodels scipy openpyxl
```

### Çalıştırma
1. Terminal/komut satırını açın
2. Proje klasörüne gidin:
   ```bash
   cd "proje_klasörünün_yolu"
   ```
3. Scripti çalıştırın:
   ```bash
   python3 ekonometri_analiz.py
   ```
4. Script çalışınca:
   - Ekranda tüm sonuçları göreceksiniz
   - `analiz_sonuclari.txt` dosyası güncellenecek
   - `grafikler/` klasörüne tüm grafikler kaydedilecek

> ⚠️ **ÖNEMLİ:** `Enflasyon verileri1.xlsx` dosyası `ekonometri_analiz.py` ile **aynı klasörde** olmalı!

---

## 📝 Word Dosyası Nasıl Hazırlanır?

### Kapak Sayfası
```
IST3102 Ekonometri Dersi - Dönem Projesi (2025-2026)

Proje Başlığı:
"Türkiye'de TÜFE Enflasyonunun Makroekonomik Belirleyicileri:
Ekonometrik Bir Analiz (2015-2023)"

Grup No: [Grup numaranız]
Grup Üyeleri:
- [İsim Soyisim] - [Öğrenci No]
- [İsim Soyisim] - [Öğrenci No]
- [İsim Soyisim] - [Öğrenci No]

Tarih: Haziran 2026
```

### Önerilen Word İçindekiler Sırası

| Bölüm | Word'e Ne Yazılacak | Grafik Eklenecek mi? |
|-------|---------------------|---------------------|
| 1. Giriş | Amaç, veri seti açıklaması, değişken tanımları | Hayır |
| 2. Tanımlayıcı İstatistikler | Ortalama, std, min, max tablosu | Evet: `tum_degiskenler.png`, `korelasyon_matrisi.png` |
| 3. Fonksiyonel Form | 4 model karşılaştırma tablosu + yorum | Evet: `fonksiyonel_form_karsilastirma.png` |
| 4. t ve F Testleri | Her değişken için hipotez + sonuç | Hayır |
| 5. MWD Testi | Hipotez + Z1, Z2 sonuçları | Hayır |
| 6. Çoklu Doğrusal Bağlantı | VIF tablosu + korelasyon tablosu | Hayır |
| 7. Birim Kök Testi (ADF) | Her değişken için ADF tablosu | Hayır |
| 8. Wald Testi | 3 kısıtlama testi | Hayır |
| 9. Chow Testi | 2018 krizi + COVID kırılması | Hayır |
| 10. Park Testi | 4 değişken için tablo | Evet: `degisen_varyans_grafikleri.png` |
| 11. Goldfeld-Quandt | 4 değişken için tablo | Hayır |
| 12. White Testi | LM ve F sonuçları | Hayır |
| 13. Durbin-Watson | DW + Durbin h sonuçları | Evet: `otokorelasyon_grafikleri.png` |
| 14. Sonuç | Özet tablo + genel değerlendirme | Evet: `diagnostik_grafikler.png` |

---

## 🎓 Her Test İçin Sunum Rehberi

Aşağıda her test için **ne söylemeniz gerektiğini**, **hipotezleri** ve **sonuçları nasıl yorumlayacağınızı** bulabilirsiniz.

---

### 1️⃣ Tanımlayıcı İstatistikler ve Grafikler

**Sunumda söylenecek:**
> "Verimiz 2015 Nisan - 2023 Temmuz arasını kapsayan 100 aylık gözlemden oluşmaktadır. Bağımlı değişkenimiz TÜFE, bağımsız değişkenlerimiz USD dolar kuru, Sanayi Üretim Endeksi, M3 para arzı ve Tüketici Güven Endeksi'dir."

**Grafikler hakkında:**
> "Grafiklerden görüldüğü üzere TÜFE ve USD özellikle 2018 sonrası hızla yükselmiştir. M3 para arzı sürekli artış gösterirken, tüketici güveni düşüş eğilimindedir."

---

### 2️⃣ Fonksiyonel Form Karşılaştırması

**Sunumda söylenecek:**
> "4 farklı fonksiyonel form tahmin ettik: Lin-Lin, Log-Log, Log-Lin ve Lin-Log. Aynı bağımlı değişkene sahip modeller kendi aralarında karşılaştırılabilir. Y bağımlı modellerde Lin-Lin (Adj.R²=0.87), lnY bağımlı modellerde Log-Lin (Adj.R²=0.90) en iyi performansı göstermiştir."

**Dikkat:** R²'leri farklı bağımlı değişkenli modeller arasında **doğrudan karşılaştıramazsınız**. Hoca bunu sorabilir!

---

### 3️⃣ t Testi

**Her değişken için şablonu kullanın:**

```
H₀: βᵢ = 0 (Değişken TÜFE üzerinde etkisizdir)
H₁: βᵢ ≠ 0 (Değişken TÜFE üzerinde etkilidir)
```

**Sonuçlar:**
| Değişken | t-ist. | p-değeri | Karar | Açıklama |
|----------|--------|----------|-------|----------|
| USD | 10.00 | 0.000 | H₀ RED | Dolar kuru enflasyonu anlamlı etkiler |
| Sanayi | 0.32 | 0.752 | H₀ Reddedilemez | Sanayi üretimi anlamsız |
| M3 | -8.14 | 0.000 | H₀ RED | Para arzı anlamlı (ama katsayı negatif — multicollinearity yüzünden) |
| Tük.Güven | 1.12 | 0.265 | H₀ Reddedilemez | Tüketici güveni anlamsız |

**Hoca sorarsa:** "M3 katsayısı neden negatif?" → "USD ile M3 arasında 0.99 korelasyon var, bu çoklu doğrusal bağlantı katsayı işaretini bozuyor."

---

### 4️⃣ F Testi

```
H₀: β₁ = β₂ = β₃ = β₄ = 0 (Model anlamsızdır)
H₁: En az bir βᵢ ≠ 0 (Model anlamlıdır)
```

> "F-istatistiğimiz 164.58, p-değeri neredeyse sıfır. F-kritik değer 2.47. F-ist > F-kritik olduğundan **H₀ reddedilir**, model bütün olarak anlamlıdır."

---

### 5️⃣ MWD Testi

**Sunumda söylenecek:**
> "MWD testinde hem doğrusal hem logaritmik model reddedildi. Bu, veri yapısının tam olarak ne doğrusal ne de logaritmik olduğunu gösteriyor. Semi-log (Log-Lin) form daha uygun olabilir."

```
Test 1 → H₀: Doğrusal model doğrudur → REDDEDİLDİ (p=0.019)
Test 2 → H₀: Logaritmik model doğrudur → REDDEDİLDİ (p=0.003)
```

---

### 6️⃣ Çoklu Doğrusal Bağlantı (Multicollinearity)

**Sunumda söylenecek:**
> "VIF analizi sonucunda USD (VIF=108) ve M3 (VIF=97) için ciddi çoklu doğrusal bağlantı tespit edildi. Bu iki değişken arasındaki korelasyon 0.99'dur. Kural olarak VIF > 10 ciddi sorun demektir."

**Hoca sorarsa çözüm önerileri:**
1. Değişkenlerden birini çıkarmak
2. Ridge regresyon kullanmak
3. PCA uygulamak

---

### 7️⃣ Birim Kök Testi (ADF)

```
H₀: Seri birim kök içerir (durağan DEĞİLDİR)
H₁: Seri durağandır
```

> "Tüm değişkenler düzey değerlerinde durağan değildir. Bu, sahte regresyon (spurious regression) riskine işaret eder. Birinci fark alındığında USD, Sanayi ve Tüketici Güven durağan hale gelmiştir."

**Dikkat:** Hoca "serilerin durağan olmaması modeli nasıl etkiler?" diye sorabilir → "Durağan olmayan serilerle yapılan regresyon sahte ilişkiler verebilir, t ve F testleri güvenilir olmayabilir."

---

### 8️⃣ Wald Testi

**Sunumda söylenecek:**
> "Wald testi ile değişkenleri gruplar halinde test ettik. Parasal değişkenler (USD + M3) birlikte anlamlıdır (p=0.000). Reel ekonomi değişkenleri (Sanayi + Tüketici Güven) ise birlikte anlamsızdır (p=0.534). Bu, Türkiye'de enflasyonun ağırlıklı olarak parasal ve kur kaynaklı olduğunu gösteriyor."

---

### 9️⃣ Chow Testi

```
H₀: Yapısal kırılma yoktur (parametreler stabildir)
H₁: Yapısal kırılma vardır
```

> "2018 Ağustos TL krizi (F=4.02, p=0.002) ve COVID-19 pandemisi (F=4.58, p=0.001) dönemlerinde yapısal kırılma tespit edilmiştir. Her iki dönemde de enflasyon modelinin parametreleri önemli ölçüde değişmiştir."

---

### 🔟 Park Testi

```
H₀: Sabit varyans (Homoscedasticity)
H₁: Değişen varyans (Heteroscedasticity)

Yöntem: ln(eᵢ²) = α + β·ln(Xⱼ) regresyonunda β anlamlı mı?
```

> "4 değişkenin tamamı için değişen varyans tespit edildi. Bu, hata terimlerinin varyansının sabit olmadığını gösteriyor."

---

### 1️⃣1️⃣ Goldfeld-Quandt Testi

```
H₀: σ₁² = σ₂² (varyanslar eşit)
H₁: σ₁² ≠ σ₂² (varyanslar eşit değil)
```

> "Veriyi her değişkene göre sıralayıp ikiye böldük. Tüm değişkenler için iki grubun varyansları farklı çıktı → değişen varyans var."

---

### 1️⃣2️⃣ White Testi

```
H₀: Sabit varyans
H₁: Değişen varyans
```

> "White LM istatistiği 81.78, p-değeri 0.000. Park ve Goldfeld-Quandt testleriyle tutarlı olarak değişen varyans tespit edilmiştir. Çözüm olarak robust (HAC) standart hatalar kullanılabilir."

---

### 1️⃣3️⃣ Durbin-Watson Testi

> "DW istatistiğimiz 0.448. Kritik değerler: dL=1.592, dU=1.758. DW < dL olduğundan **pozitif otokorelasyon** vardır. DW'nin 0'a yakın olması güçlü pozitif otokorelasyona işaret eder."

### Durbin h Testi

> "Gecikmeli bağımlı değişken eklenen modelde Durbin h = 4.14. |h| > 1.96 olduğundan otokorelasyon bu modelde de devam etmektedir."

---

## 🎤 Sunum İpuçları

### Slayt Yapısı Önerisi
1. **Kapak** (1 slayt)
2. **Veri Seti Tanıtımı** (1-2 slayt) — grafik göster
3. **Model ve Fonksiyonel Form** (2 slayt) — tablo + grafik
4. **t ve F Testleri** (2 slayt) — tablo
5. **MWD Testi** (1 slayt)
6. **Multicollinearity** (1 slayt) — VIF tablosu
7. **Birim Kök (ADF)** (1 slayt) — tablo
8. **Wald Testi** (1 slayt)
9. **Chow Testi** (1 slayt)
10. **Değişen Varyans (Park + GQ + White)** (2 slayt) — grafik ekle
11. **Otokorelasyon (DW + h)** (1-2 slayt) — grafik ekle
12. **Sonuç ve Özet Tablo** (1-2 slayt)

### Sık Sorulan Sorular ve Cevaplar

**S: R² nedir?**
> Bağımsız değişkenlerin, bağımlı değişkendeki değişimin yüzde kaçını açıkladığını gösterir. R²=0.87 → %87'si açıklanıyor.

**S: Neden bazı değişkenler anlamsız?**
> Sanayi üretimi ve tüketici güveni tek başına enflasyonu istatistiksel olarak anlamlı düzeyde açıklayamamaktadır. Ancak bu, teorik olarak ilişki olmadığı anlamına gelmez; multicollinearity de etkili olabilir.

**S: M3'ün katsayısı neden negatif?**
> USD ile M3 arasında 0.99 korelasyon var. Bu ciddi çoklu doğrusal bağlantı, katsayı işaretlerini bozabiliyor. Tek başına modele konduğunda M3 pozitif etkili çıkar.

**S: Neden değişen varyans var?**
> Türkiye gibi gelişmekte olan ülkelerde enflasyon düşükken az, yüksekken çok dalgalanır. Bu doğal olarak değişen varyansa yol açar.

**S: Neden otokorelasyon var?**
> Enflasyon doğası gereği ataleti olan (persistent) bir değişkendir. Bu ayın enflasyonu geçen ayla yüksek korelasyona sahiptir. Zaman serisi modellerinde bu yaygındır.

**S: Durağanlık neden önemli?**
> Durağan olmayan serilerle regresyon yapılırsa "sahte regresyon" riski doğar — aslında ilişkisiz değişkenler arasında anlamlı ilişki bulunabilir.

---

## ⚡ Hızlı Başvuru: Tüm Hipotezler

| # | Test | H₀ | H₁ | Sonuç |
|---|------|----|----|-------|
| 1 | t (USD) | β₁ = 0 | β₁ ≠ 0 | **RED** |
| 2 | t (Sanayi) | β₂ = 0 | β₂ ≠ 0 | Reddedilemez |
| 3 | t (M3) | β₃ = 0 | β₃ ≠ 0 | **RED** |
| 4 | t (Tük.Güven) | β₄ = 0 | β₄ ≠ 0 | Reddedilemez |
| 5 | F | β₁=β₂=β₃=β₄=0 | En az bir βᵢ≠0 | **RED** |
| 6 | MWD (Lin) | Doğrusal model doğru | Log model doğru | **RED** |
| 7 | MWD (Log) | Log model doğru | Doğrusal model doğru | **RED** |
| 8 | ADF (tüm) | Birim kök var | Durağan | Reddedilemez |
| 9 | Wald (Parasal) | β₁=β₃=0 | En az biri ≠0 | **RED** |
| 10 | Wald (Reel) | β₂=β₄=0 | En az biri ≠0 | Reddedilemez |
| 11 | Chow (2018) | Kırılma yok | Kırılma var | **RED** |
| 12 | Chow (COVID) | Kırılma yok | Kırılma var | **RED** |
| 13 | Park | Sabit varyans | Değişen varyans | **RED** |
| 14 | Goldfeld-Quandt | σ₁²=σ₂² | σ₁²≠σ₂² | **RED** |
| 15 | White | Sabit varyans | Değişen varyans | **RED** |
| 16 | Durbin-Watson | ρ=0 (otokor. yok) | ρ≠0 | **RED** |
| 17 | Durbin h | Otokor. yok | Otokor. var | **RED** |

---

## 📦 Teslim Kontrol Listesi

Teslim dosyanızda şunlar olmalı:

- [ ] **Excel dosyası:** `Enflasyon verileri1.xlsx`
- [ ] **Word dosyası** (kapak sayfasında isimler + numaralar)
  - [ ] Tüm testler ve hipotezler yazılmış
  - [ ] Her test için yorum yapılmış
  - [ ] Grafikler eklenmiş
  - [ ] Tablolar düzenli
- [ ] Dosya adı formatı: `Grupid_GrupLiderSoyad_Econometrics.zip`
  - Örnek: `Group77_Parim_Econometrics.zip`
- [ ] Teslim tarihi: **12.06.2025 - 23:59** (online.yildiz.edu.tr)
- [ ] Sadece grup lideri yükleyebilir!

---

*Bu rehber IST3102 Ekonometri projesi için hazırlanmıştır. Sorularınız olursa analiz_sonuclari.txt dosyasındaki detaylı çıktılara başvurabilirsiniz.*
