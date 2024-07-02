import sys,requests,nltk,os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider, QScrollArea, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont , QIcon

# NLTK için veri indirme
nltk.download('punkt')
nltk.download('stopwords')

# TMDb Veritabanı API Anahtarı
api_key = '587584a7114cd0dbbd7e4f82e91128de'  

class Filmoneriuygulamasi(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Filmoneriler')
        self.setGeometry(100, 100, 900, 700)  # Pencere boyutları 

        # Ana Düzen 
        duzen = QVBoxLayout()

        # Başlık
        self.baslik = QLabel('Film Önerileri', self)
        self.baslik.setFont(QFont('Garamond', 28))
        self.baslik.setAlignment(Qt.AlignCenter)

        # Uygulama İkonu
        konum_dizin = os.path.dirname(os.path.abspath(__file__))
        konum = os.path.join(konum_dizin , 'curtain.png')
        self.setWindowIcon(QIcon(konum))

        # Arama çubuğu
        self.label = QLabel('Ne Tür Bir Film izlemek istersiniz:')
        self.metin_kutusu = QLineEdit(self)

        # Türleri gösterme düğmesi
        self.etiket_goster_dugmesi = QPushButton('Aranılabilecek Türleri Gör', self)
        self.etiket_goster_dugmesi.clicked.connect(self.mevcut_turleri_goster)

        # IMDb puanı aralığı 
        self.imdb_puan_aralik = QLabel('IMDb Puanı')
        self.imdb_baslangic_puan = QLabel("En Düşük Puan")
        self.imdb_bitis_puan = QLabel("En Yüksek Puan")

        # IMDb puanı aralığı sürgüleri
        self.imdb_surgu_baslangic = QSlider(Qt.Horizontal, self)
        self.imdb_surgu_baslangic.setRange(0, 100)  # 0.0 ile 10.0 arası
        self.imdb_surgu_baslangic.setValue(60)  # Uygulama açıldığındaki başlangıç değeri
        self.imdb_surgu_baslangic.valueChanged.connect(self.imdb_baslangic_deger)

        self.imdb_surgu_bitis = QSlider(Qt.Horizontal, self)
        self.imdb_surgu_bitis.setRange(0, 100)  
        self.imdb_surgu_bitis.setValue(100)  # Uygulama açıldığındaki bitiş değeri 
        self.imdb_surgu_bitis.valueChanged.connect(self.imdb_bitis_deger)

        self.imdb_baslangic_deger = QLabel(str(self.imdb_surgu_baslangic.value() / 10))  
        self.imdb_bitis_deger = QLabel(str(self.imdb_surgu_bitis.value() / 10))  

        # IMDB düzeni
        imdb_duzen = QHBoxLayout()
        imdb_duzen.addWidget(self.imdb_baslangic_puan)
        imdb_duzen.addWidget(self.imdb_surgu_baslangic)
        imdb_duzen.addWidget(self.imdb_baslangic_deger)
        imdb_duzen.addWidget(self.imdb_bitis_puan)
        imdb_duzen.addWidget(self.imdb_surgu_bitis)
        imdb_duzen.addWidget(self.imdb_bitis_deger)

        # Tarih aralığı 
        self.tarih_aralik = QLabel('Çıkış Tarihi:')
        self.tarih_baslangic_yili = QLabel('Başlangıç Yılı:')
        self.tarih_bitis_yili = QLabel('Bitiş Yılı:')

        # Tarih aralığı sürgüleri
        self.tarih_surgu_baslangic = QSlider(Qt.Horizontal, self)
        self.tarih_surgu_baslangic.setRange(1900, 2024)  
        self.tarih_surgu_baslangic.setValue(2000)
        self.tarih_surgu_baslangic.valueChanged.connect(self.tarih_baslangic_deger_guncelleme)

        self.tarih_surgu_bitis = QSlider(Qt.Horizontal, self)
        self.tarih_surgu_bitis.setRange(1900, 2024)  
        self.tarih_surgu_bitis.setValue(2020)
        self.tarih_surgu_bitis.valueChanged.connect(self.tarih_bitis_deger_guncelleme)

        # Tarih aralığı sürgüleri belirteç
        self.tarih_baslangic_deger = QLabel(str(self.tarih_surgu_baslangic.value()))
        self.tarih_bitis_deger = QLabel(str(self.tarih_surgu_bitis.value()))

        # Tarih sürgülerinin yatay düzeni
        tarih_duzen = QHBoxLayout()
        tarih_duzen.addWidget(self.tarih_baslangic_yili)
        tarih_duzen.addWidget(self.tarih_surgu_baslangic)
        tarih_duzen.addWidget(self.tarih_baslangic_deger)
        tarih_duzen.addWidget(self.tarih_bitis_yili)
        tarih_duzen.addWidget(self.tarih_surgu_bitis)
        tarih_duzen.addWidget(self.tarih_bitis_deger)

        # Arama düğmesi
        self.arama_dugmesi = QPushButton('Ara', self)
        self.arama_dugmesi.clicked.connect(self.film_arama)
        self.arama_dugmesi.setStyleSheet("background-color: #3498db; color: white; padding: 10px; font-size: 14px; border-radius: 5px;")

        # Sonuç Gösterme Alanı
        self.kaydirma_alani = QScrollArea(self)
        self.kaydirma_alani.setWidgetResizable(True)
        self.kaydirma_icerik = QWidget(self.kaydirma_alani)
        self.kaydirma_duzen = QVBoxLayout(self.kaydirma_icerik)
        self.kaydirma_alani.setWidget(self.kaydirma_icerik)

        # Düzen
        duzen.addWidget(self.baslik)
        duzen.addWidget(self.label)
        duzen.addWidget(self.metin_kutusu)
        duzen.addWidget(self.etiket_goster_dugmesi)
        duzen.addWidget(self.imdb_puan_aralik)
        duzen.addLayout(imdb_duzen)
        duzen.addWidget(self.tarih_aralik)
        duzen.addLayout(tarih_duzen)
        duzen.addWidget(self.arama_dugmesi)
        duzen.addWidget(self.kaydirma_alani)

        self.setLayout(duzen)

        # Pencereyi Yansıt
        self.show()

    # Değer Güncellemeler
    
    def tarih_baslangic_deger_guncelleme(self, value):
        self.tarih_baslangic_deger.setText(str(value))

    def tarih_bitis_deger_guncelleme(self, value):
        self.tarih_bitis_deger.setText(str(value))

    def imdb_baslangic_deger(self, value):
        self.imdb_baslangic_deger.setText(str(value / 10))

    def imdb_bitis_deger(self, value):
        self.imdb_bitis_deger.setText(str(value / 10))

    # Aratılan kelime optimizasyonu

    def kelimeleri_duzenleme(self, kullanici_girisi):
        
        
        ayirt_edilenler = [',', ';', ' ve ', ' ile ', ' - ']
        duraklama_kelimeleri = set(stopwords.words('turkish'))

        for ayirici in ayirt_edilenler:
            kullanici_girisi = kullanici_girisi.replace(ayirici, ' ')

        kelime_tokenlestir = word_tokenize(kullanici_girisi, language='turkish')
        duzenlenmis_kelimeler = [kelime for kelime in kelime_tokenlestir if not kelime.lower() in duraklama_kelimeleri and kelime.isalnum()]

        return duzenlenmis_kelimeler

    # Aranabilecek Türler

    def mevcut_turleri_goster(self):
        
        mevcut_turler = (
            "Aksiyon, Komedi, Dram, Korku, Bilim Kurgu, Romantik,\n"
            "Gerilim, Fantastik, Animasyon, Gizem, Macera, Suç,\n"
            "Belgesel, Savaş, Vahşi Batı, Müzik, Aile,\n"
            "Tarih, Müzik, TV Filmi"
        )
        QMessageBox.information(self, "Mevcut Türler", mevcut_turler)

    #Film Aratma

    def film_arama(self):
        kullanici_girisi = self.metin_kutusu.text()
        baslangic_tarih = self.tarih_surgu_baslangic.value()
        bitis_tarih = self.tarih_surgu_bitis.value()
        imdb_baslangic = self.imdb_surgu_baslangic.value() / 10
        imdb_bitis = self.imdb_surgu_bitis.value() / 10
        anahtar_kelimeler = self.kelimeleri_duzenleme(kullanici_girisi)

        if anahtar_kelimeler:
            filmtur_id = self.get_filmturler(anahtar_kelimeler)
            if filmtur_id:
                filmler = self.veritabani_sorgula(filmtur_id, baslangic_tarih, bitis_tarih, imdb_baslangic, imdb_bitis)

                # Sonuçları temizleme
                for i in reversed(range(self.kaydirma_duzen.count())):
                    widget = self.kaydirma_duzen.itemAt(i).widget()
                    if widget is not None:
                        widget.deleteLater()

                if filmler:
                    self.kaydirma_duzen.addWidget(QLabel(f"Anahtar Kelimeler: {', '.join(anahtar_kelimeler)}\n"))

                    for film in filmler['results']:
                        self.filmi_sonuclara_ekle(film)
                else:
                    self.kaydirma_duzen.addWidget(QLabel("Uygun film bulunamadı."))
            else:
                self.kaydirma_duzen.addWidget(QLabel("Girilen aramalarla eşleşen bir tür bulunamadı."))
        else:
            self.kaydirma_duzen.addWidget(QLabel("Lütfen geçerli film türü girin."))

    def filmi_sonuclara_ekle(self, film):
        
        filmi_verisi = QFrame(self)
        filmi_duzen = QHBoxLayout(filmi_verisi)

        # Kapak resmi ekleme
        poster_label = QLabel(self)
        poster_label.setFixedSize(100, 150)
        poster_path = film.get('poster_path', None)
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(poster_url).content)
            poster_label.setPixmap(pixmap.scaled(poster_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Film bilgileri
        film_bilgi = QLabel(self)
        film_bilgi_metni = f"Başlık: {film['title']}\nÇıkış Tarihi: {film.get('release_date', 'Tarih Bilinmiyor')}\nIMDb Puanı: {film.get('vote_average', 'Puan Bilinmiyor')}\n"

        # Filmin kısa özeti
        overview = film.get('overview', 'Özet mevcut değil.')
        film_bilgi_metni += f"Özet: {overview[:450]}..."  # 450 karakterlik sınır özet için


        film_bilgi.setText(film_bilgi_metni)
        film_bilgi.setWordWrap(True)

        filmi_duzen.addWidget(poster_label)
        filmi_duzen.addWidget(film_bilgi)

        self.kaydirma_duzen.addWidget(filmi_verisi)
    
    
    # Bilgileri Çekme


    def get_filmturler(self, anahtar_kelimeler):
        
        
        url = f"https://api.themoviedb.org/3/genre/movie/list?api_key=587584a7114cd0dbbd7e4f82e91128de&language=tr-TR"
        response = requests.get(url)
        if response.status_code == 200:
            genres = response.json().get('genres', [])
            matched_genre_ids = [genre['id'] for genre in genres if any(keyword.lower() in genre['name'].lower() for keyword in anahtar_kelimeler)]
            return ','.join(map(str, matched_genre_ids)) if matched_genre_ids else None
        else:
            return None

    
    def veritabani_sorgula(self, filmtur_id, baslangic_tarih, bitis_tarih, imdb_baslangic, imdb_bitis):
        
        
        url = f"https://api.themoviedb.org/3/discover/movie?api_key=587584a7114cd0dbbd7e4f82e91128de&with_genres={filmtur_id}&primary_release_date.gte={baslangic_tarih}-01-01&primary_release_date.lte={bitis_tarih}-12-31&vote_average.gte={imdb_baslangic}&vote_average.lte={imdb_bitis}&language=tr-TR"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

if __name__ == '__main__':
    uygulama = QApplication(sys.argv)
    baslat = Filmoneriuygulamasi()
    sys.exit(uygulama.exec_())