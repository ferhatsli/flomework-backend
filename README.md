# Flalingo - Kişiselleştirilmiş Dil Öğrenme Testleri

Bu proje, Zoom üzerinden gerçekleştirilen İngilizce derslerinin transkriptlerini analiz ederek kişiselleştirilmiş, kısa ve interaktif soru-cevap tarzı testler oluşturan bir sistemdir.

## Özellikler

- Zoom ders transkriptlerinin analizi
- Yapay zeka ile kişiselleştirilmiş test oluşturma
- İnteraktif ve eğlenceli öğrenme deneyimi

## Kurulum

1. Gerekli kütüphaneleri yükleyin:

   ```
   pip install -r requirements.txt
   ```

2. `.env` dosyasını oluşturun ve API anahtarlarınızı ekleyin:

   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. Uygulamayı çalıştırın:
   ```
   python app.py
   ```

## Kullanım

1. Zoom ders transkriptini sisteme yükleyin.
2. Yapay zeka, transkripti analiz ederek kişiselleştirilmiş testler oluşturacaktır.
3. Oluşturulan testleri çözün ve dil becerilerinizi geliştirin.

## Teknolojiler

- Python
- Flask
- Gemini 1.5 Flash API
- Pandas
