import requests

def indirimleri_getir():
    # Steam ana sayfa vitrin verisi (Türkiye fiyatları)
    url = "https://store.steampowered.com/api/featuredcategories?l=turkish&cc=tr"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        firsatlar = []
        eklenen_oyunlar = set() 

        tum_kategoriler = []
        
        if isinstance(data, dict):
            tum_kategoriler.extend(data.values())
            
        if "featured_win" in data:
            tum_kategoriler.extend(data["featured_win"])

        for kategori in tum_kategoriler:
            if isinstance(kategori, dict) and "items" in kategori:
                for oyun in kategori["items"]:
                    try:
                        indirim = oyun.get('discount_percent', 0)
                        
                        # --- BURAYI DEĞİŞTİRDİK: ARTIK %10 VE ÜZERİNİ ALIYOR ---
                        if indirim >= 10:
                            oyun_id = oyun.get('id')
                            
                            if oyun_id not in eklenen_oyunlar:
                                eski_fiyat = oyun.get('original_price', 0) / 100
                                yeni_fiyat = oyun.get('final_price', 0) / 100
                                
                                oyun_bilgisi = {
                                    "ad": oyun['name'],
                                    "eski_fiyat": eski_fiyat,
                                    "yeni_fiyat": yeni_fiyat,
                                    "indirim_orani": indirim,
                                    "resim": oyun.get('large_capsule_image', ''),
                                    "link": f"https://store.steampowered.com/app/{oyun_id}/"
                                }
                                firsatlar.append(oyun_bilgisi)
                                eklenen_oyunlar.add(oyun_id)
                                
                    except Exception as e:
                        continue 

        # Yine de en yüksek indirimi en üste koyacak şekilde sıralayalım
        firsatlar.sort(key=lambda x: x['indirim_orani'], reverse=True)
        
        return firsatlar

    except Exception as e:
        print(f"Hata oluştu: {e}")
        return []

if __name__ == "__main__":
    oyunlar = indirimleri_getir()
    print(f"--- {len(oyunlar)} ADET FIRSAT BULUNDU ---")
    
    for oyun in oyunlar[:5]: 
        print(f"🎮 {oyun['ad']}")
        print(f"📉 İndirim: %{oyun['indirim_orani']}")
        print("-" * 20)