# 🎮 Steam Fırsatçısı Botu (Steam Deal Hunter)

**Steam Fırsatçısı**, Steam üzerindeki oyun indirimlerini takip eden, dolar kurunu anlık olarak TL'ye çeviren ve Twitter (X) üzerinde otomatik paylaşım yapan Python tabanlı bir bottur.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Status](https://img.shields.io/badge/Status-Active-success)

## 🚀 Özellikler

* **Veri Madenciliği:** Steam API üzerinden anlık indirimleri tarar.
* **Akıllı Filtreleme:** * **VIP:** %30 ve üzeri indirimleri özel görselle tekli paylaşır.
    * **Toplu Liste:** %10-%30 arası indirimleri "Gözden Kaçanlar" listesi olarak paylaşır.
* **Döviz Çevirici:** Anlık USD/TRY kurunu çekerek fiyatı hesaplar.
* **Görsel İşleme:** Pillow kütüphanesi ile oyun kapaklarına dinamik fiyat etiketi basar.
* **Twitter Otomasyonu:** API v2 ile otomatik tweet atar.

## 🛠️ Kurulum

1.  Repoyu klonlayın:
    ```bash
    git clone [https://github.com/OrkunKarabay/SteamBot.git](https://github.com/KULLANICIADIN/SteamBot.git)
    cd SteamBot
    ```

2.  Gereksinimleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```

3.  Ayarları yapın:
    * `config_template.py` dosyasının adını `config.py` yapın.
    * İçerisine Twitter Developer Portal'dan aldığınız API anahtarlarını girin.

4.  Çalıştırın:
    ```bash
    python main.py
    ```

## 🤖 Kullanılan Teknolojiler

* **Python 3**
* **Tweepy** (Twitter API)
* **Pillow (PIL)** (Görsel İşleme)
* **Requests** (API İstekleri)

---
*Bu proje eğitim ve portfolyo amacıyla açık kaynak olarak paylaşılmıştır.*
