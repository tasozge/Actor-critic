import numpy as np
import pygame
import time

class AsansorAktorKritik:
    def __init__(self):
        # Asansör durumu için parametreler
        self.mevcut_kat = 0
        self.hedef_kat = 0
        self.yolcu_sayisi = 0
        self.max_kat = 10
        
        # Aktör ve Kritik için öğrenme oranları
        self.aktor_ogrenme_orani = 0.01
        self.kritik_ogrenme_orani = 0.01
        
        # Politika parametreleri
        self.aktor_parametreleri = np.random.rand(4)
        self.kritik_parametreleri = np.random.rand(4)
        
    def durum_ozelliklerini_al(self):
        # Durumu temsil eden özellikler
        kat_farki = abs(self.hedef_kat - self.mevcut_kat)
        enerji_tuketimi = kat_farki * (0.1 + 0.02 * self.yolcu_sayisi)
        bekleme_zamani = kat_farki * 2
        
        return np.array([
            kat_farki / self.max_kat,
            self.yolcu_sayisi / 8,
            enerji_tuketimi / 10,
            bekleme_zamani / 30
        ])
    
    def aktor_eylem_sec(self, ozellikler):
        # Politika fonksiyonu
        eylem_skoru = np.dot(self.aktor_parametreleri, ozellikler)
        eylem_olasiligi = 1 / (1 + np.exp(-eylem_skoru))
        return 1 if np.random.random() < eylem_olasiligi else 0
    
    def kritik_deger_tahmin(self, ozellikler):
        return np.dot(self.kritik_parametreleri, ozellikler)
    
    def egit(self, durum, eylem, odul, yeni_durum):
        # TD hatası hesapla
        mevcut_deger = self.kritik_deger_tahmin(durum)
        yeni_deger = self.kritik_deger_tahmin(yeni_durum)
        td_hata = odul + 0.95 * yeni_deger - mevcut_deger
        
        # Kritik güncelleme
        self.kritik_parametreleri += self.kritik_ogrenme_orani * td_hata * durum
        
        # Aktör güncelleme
        eylem_gradyani = eylem - (1 / (1 + np.exp(-np.dot(self.aktor_parametreleri, durum))))
        self.aktor_parametreleri += self.aktor_ogrenme_orani * td_hata * eylem_gradyani * durum

class AsansorGorsel:
    def __init__(self, max_kat):
        pygame.init()
        self.max_kat = max_kat
        self.genislik = 800
        self.yukseklik = 600
        self.ekran = pygame.display.set_mode((self.genislik, self.yukseklik))
        pygame.display.set_caption("Asansör Aktör-Kritik Simülasyonu")
        
        # Renkler
        self.BEYAZ = (255, 255, 255)
        self.SIYAH = (0, 0, 0)
        self.KIRMIZI = (255, 0, 0)
        self.YESIL = (0, 255, 0)
        self.MAVI = (0, 0, 255)
        
        # Asansör boyutları
        self.bina_x = 300
        self.bina_genislik = 200
        self.kat_yukseklik = 50
        
    def ekrani_guncelle(self, asansor, odul):
        self.ekran.fill(self.BEYAZ)
        
        # Bina çiz
        pygame.draw.rect(self.ekran, self.SIYAH, 
                        (self.bina_x, 50, self.bina_genislik, 
                         (self.max_kat + 1) * self.kat_yukseklik), 2)
        
        # Katları çiz
        for kat in range(self.max_kat + 1):
            y = 50 + kat * self.kat_yukseklik
            pygame.draw.line(self.ekran, self.SIYAH, 
                           (self.bina_x, y), 
                           (self.bina_x + self.bina_genislik, y))
            
            # Kat numaralarını yaz
            font = pygame.font.Font(None, 36)
            text = font.render(str(kat), True, self.SIYAH)
            self.ekran.blit(text, (self.bina_x - 30, y - 10))
        
        # Asansörü çiz
        asansor_y = 50 + (self.max_kat - asansor.mevcut_kat) * self.kat_yukseklik
        pygame.draw.rect(self.ekran, self.MAVI,
                        (self.bina_x + 50, asansor_y - 40, 100, 40))
        
        # Hedef katı işaretle
        hedef_y = 50 + (self.max_kat - asansor.hedef_kat) * self.kat_yukseklik
        pygame.draw.circle(self.ekran, self.KIRMIZI,
                         (self.bina_x + 20, hedef_y), 10)
        
        # Bilgileri göster
        bilgiler = [
            f"Mevcut Kat: {asansor.mevcut_kat}",
            f"Hedef Kat: {asansor.hedef_kat}",
            f"Yolcu Sayısı: {asansor.yolcu_sayisi}",
            f"Ödül: {odul:.2f}"
        ]
        
        for i, bilgi in enumerate(bilgiler):
            text = font.render(bilgi, True, self.SIYAH)
            self.ekran.blit(text, (20, 20 + i * 30))
        
        pygame.display.flip()

def main():
    asansor = AsansorAktorKritik()
    gorsel = AsansorGorsel(asansor.max_kat)
    
    calisiyor = True
    saat = pygame.time.Clock()
    
    while calisiyor:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisiyor = False
        
        # Yeni senaryo
        asansor.hedef_kat = np.random.randint(0, asansor.max_kat)
        asansor.yolcu_sayisi = np.random.randint(0, 8)
        
        mevcut_durum = asansor.durum_ozelliklerini_al()
        eylem = asansor.aktor_eylem_sec(mevcut_durum)
        
        # Ödül hesapla
        enerji_tuketimi = abs(asansor.hedef_kat - asansor.mevcut_kat) * (0.1 + 0.02 * asansor.yolcu_sayisi)
        bekleme_suresi = abs(asansor.hedef_kat - asansor.mevcut_kat) * 2
        odul = -(0.3 * enerji_tuketimi + 0.7 * bekleme_suresi)
        
        # Asansörü hareket ettir
        if eylem == 1:
            asansor.mevcut_kat = asansor.hedef_kat
        
        yeni_durum = asansor.durum_ozelliklerini_al()
        asansor.egit(mevcut_durum, eylem, odul, yeni_durum)
        
        # Görselleştirme
        gorsel.ekrani_guncelle(asansor, odul)
        saat.tick(1)  # 1 FPS
        time.sleep(1)  # Her senaryo arasında 1 saniye bekle
    
    pygame.quit()

if __name__ == "__main__":
    main() 