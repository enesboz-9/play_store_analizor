# AppVentures — Play Store Analizörü

**Yeni veri seti (2021) ile güncellenmiş sürüm.**

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

1. `Google-Playstore.csv` dosyasını `app.py` ile aynı klasöre koyun.
2. `googleplaystore_user_reviews.csv` dosyasını da aynı klasöre koyun.
3. Uygulamayı başlatın:

```bash
streamlit run app.py
```

## Veri Setleri

| Dosya | Açıklama | Kaynak |
|-------|----------|--------|
| `Google-Playstore.csv` | ~2.3M uygulama, 2021 (YENİ) | Kaggle |
| `googleplaystore_user_reviews.csv` | Kullanıcı yorumları | Kaggle |

## Notlar

- Uygulama hem yeni (`Google-Playstore.csv`) hem eski (`googleplaystore.csv`) formatı otomatik algılar.
- Büyük veri seti için ilk yükleme birkaç dakika sürebilir; sonrasında önbellekten hızlı çalışır.
