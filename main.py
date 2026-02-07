import requests
import tweepy
from PIL import Image, ImageDraw, ImageFont
import io 
import os
import time # Bekleme süreleri için
import steam_veri 
import config

# --- AYARLAR ---
YEDEK_KUR = 36.50 
HAFIZA_DOSYASI = "atilanlar.txt"
VIP_SINIRI = 30  # Yüzde 30 ve üzeri tek post olur
GENEL_RESIM_ADI = "genel_indirim_kapagi.jpg" # Toplu tweetler için sabit resim adı

def dolar_kuru_getir():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data["rates"]["TRY"]
    except:
        return YEDEK_KUR

def twittera_baglan():
    auth = tweepy.OAuth1UserHandler(
        config.api_key, config.api_secret,
        config.access_token, config.access_token_secret
    )
    api = tweepy.API(auth)
    client = tweepy.Client(
        consumer_key=config.api_key,
        consumer_secret=config.api_secret,
        access_token=config.access_token,
        access_token_secret=config.access_token_secret
    )
    return api, client

def kapak_resmini_indir(url):
    try:
        response = requests.get(url)
        image_bytes = io.BytesIO(response.content)
        img = Image.open(image_bytes)
        return img
    except:
        return None

# --- YENİ FONKSİYON: SABİT KAPAK RESMİ OLUŞTUR ---
def sabit_resim_olustur():
    """Çıtır listeler için bir kez çalışıp sabit bir kapak resmi üretir."""
    if os.path.exists(GENEL_RESIM_ADI):
        return # Resim zaten varsa tekrar yapma

    print("⚙️ Sabit kapak resmi oluşturuluyor...")
    # Koyu mavi/mor bir arka plan oluştur (600x300px)
    img = Image.new('RGB', (600, 300), color=(30, 30, 60))
    d = ImageDraw.Draw(img)
    
    try:
        # Kalın bir font bulmaya çalışalım
        font_baslik = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 45, index=1) # Bold
        font_alt = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    except:
        font_baslik = ImageFont.load_default()
        font_alt = ImageFont.load_default()

    # Başlık ve Alt Yazı
    text1 = "GÖZDEN KAÇAN"
    text2 = "FIRSATLAR"
    text3 = "(%30 Altı İndirimler)"
    
    # Yazıları ortala ve yaz (Basitçe koordinat verdim)
    d.text((50, 80), text1, font=font_baslik, fill=(200, 200, 200)) # Açık gri
    d.text((50, 130), text2, font=font_baslik, fill=(0, 255, 0))   # Yeşil
    d.text((50, 200), text3, font=font_alt, fill="white")

    # Bir de süs olsun diye sağa basit bir yüzde işareti çizelim
    d.text((400, 50), "%", font=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 200), fill=(50, 255, 50, 50))

    img.save(GENEL_RESIM_ADI)
    print("✅ Sabit resim oluşturuldu.")

def resim_uzerine_yaz(img, oyun, tl_fiyat):
    d = ImageDraw.Draw(img)
    genislik, yukseklik = img.size
    
    try:
        font_buyuk = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        font_buyuk = ImageFont.load_default()

    d.rectangle([(0, yukseklik - 120), (genislik, yukseklik)], fill="black")
    
    indirim_metni = f"-{oyun['indirim_orani']}%"
    d.text((20, yukseklik - 100), indirim_metni, font=font_buyuk, fill=(0, 255, 0)) 

    fiyat_metni = f"{tl_fiyat} TL"
    text_bbox = d.textbbox((0, 0), fiyat_metni, font=font_buyuk)
    text_width = text_bbox[2] - text_bbox[0]
    d.text((genislik - text_width - 20, yukseklik - 100), fiyat_metni, font=font_buyuk, fill="white")
    
    return img

def hafizayi_oku():
    if not os.path.exists(HAFIZA_DOSYASI):
        return []
    with open(HAFIZA_DOSYASI, "r") as f:
        return f.read().splitlines()

def hafizaya_yaz(link):
    with open(HAFIZA_DOSYASI, "a") as f:
        f.write(f"{link}\n")

# --- GÜNCELLENEN FONKSİYON: TOPLU TWEET (Artık Resimli) ---
def toplu_tweet_at(oyun_listesi, kur, client, api):
    print("🖼️ Toplu tweet için görsel hazırlanıyor...")
    tweet_metni = "🧐 GÖZDEN KAÇAN FIRSATLAR (%30 Altı)\n\n"
    
    for oyun in oyun_listesi:
        fiyat_tl = int(oyun['yeni_fiyat'] * kur)
        # Oyun adını biraz daha kısaltalım ki sığsın (20 karakter)
        ad_kisa = oyun['ad'][:20] + ".." if len(oyun['ad']) > 20 else oyun['ad']
        satir = f"🎮 {ad_kisa} | -%{oyun['indirim_orani']} | {fiyat_tl}₺\n"
        tweet_metni += satir
    
    tweet_metni += "\n#Steam #İndirim #Fırsat"
    
    try:
        # 1. Sabit resmi Twitter'a yükle (v1.1 API)
        media = api.media_upload(filename=GENEL_RESIM_ADI)
        
        # 2. Tweeti resimle birlikte at (v2 Client)
        client.create_tweet(text=tweet_metni, media_ids=[media.media_id])
        
        print("✅ TOPLU TWEET ATILDI (Resimli)")
        for oyun in oyun_listesi:
            hafizaya_yaz(oyun['link'])
    except Exception as e:
        print(f"❌ Toplu tweet hatası: {e}")

# --- ANA FONKSİYON ---
def main():
    # İlk çalışmada sabit resmi oluştur
    sabit_resim_olustur()

    print("⏳ Steam taranıyor...")
    tum_firsatlar = steam_veri.indirimleri_getir()
    
    if not tum_firsatlar:
        print("❌ İndirim bulunamadı.")
        return

    atilanlar = hafizayi_oku()
    anlik_kur = dolar_kuru_getir()
    api, client = twittera_baglan()

    vip_listesi = []   # %30 ve üstü
    citir_listesi = [] # %30 altı

    for oyun in tum_firsatlar:
        if oyun['link'] not in atilanlar:
            if oyun['indirim_orani'] >= VIP_SINIRI:
                vip_listesi.append(oyun)
            else:
                citir_listesi.append(oyun)

    # --- 1. ADIM: VIP OYUN PAYLAŞIMI ---
    if vip_listesi:
        secilen_oyun = vip_listesi[0]
        tahmini_tl = int(secilen_oyun['yeni_fiyat'] * anlik_kur)
        
        print(f"💎 VIP Oyun İşleniyor: {secilen_oyun['ad']} (-%{secilen_oyun['indirim_orani']})")
        
        orijinal_resim = kapak_resmini_indir(secilen_oyun['resim'])
        if orijinal_resim:
            islenmis_resim = resim_uzerine_yaz(orijinal_resim, secilen_oyun, tahmini_tl)
            islenmis_resim.save("temp_post.jpg")
            
            tweet = (
                f"🔥 FIRSAT ALARMI!\n\n"
                f"🎮 {secilen_oyun['ad']}\n"
                f"📉 İndirim: %{secilen_oyun['indirim_orani']}\n"
                f"💵 Fiyat: {secilen_oyun['yeni_fiyat']} $ (~{tahmini_tl} TL)\n\n"
                f"🔗 Link: {secilen_oyun['link']}\n\n"
                f"#steam #oyun #indirim"
            )
            
            try:
                media = api.media_upload(filename="temp_post.jpg")
                client.create_tweet(text=tweet, media_ids=[media.media_id])
                hafizaya_yaz(secilen_oyun['link'])
                print("✅ VIP TWEET ATILDI!")
            except Exception as e:
                print(f"❌ VIP Tweet Hatası: {e}")
        else:
            print("Resim indirilemedi.")
    else:
        print("📭 Paylaşılacak yeni Yüksek İndirim yok.")

    # --- 2. ADIM: ÇITIR LİSTE PAYLAŞIMI (Artık Resimli) ---
    if vip_listesi:
        print("⏳ Spam önleme için 10 saniye bekleniyor...")
        time.sleep(10)

    # En az 3 tane düşük indirimli oyun varsa toplu atalım
    if len(citir_listesi) >= 3:
        secilen_citirlar = citir_listesi[:4]
        # Burada artık 'api' nesnesini de gönderiyoruz
        toplu_tweet_at(secilen_citirlar, anlik_kur, client, api)
    else:
        print(f"📭 Yeterli düşük indirim yok (Şu an: {len(citir_listesi)} tane). 3 tane olunca atar.")

if __name__ == "__main__":
    main()