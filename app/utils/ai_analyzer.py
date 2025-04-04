import os
import logging
import google.generativeai as genai
from typing import Dict, List, Any
from dotenv import load_dotenv

# .env dosyasından API anahtarını yükle
load_dotenv()

# Loglama yapılandırması
logger = logging.getLogger(__name__)

class AIAnalyzer:
    """
    Transkriptleri analiz etmek ve testler oluşturmak için yapay zeka kullanır.
    """
    
    def __init__(self):
        """
        AIAnalyzer sınıfını başlatır ve Gemini API'yi yapılandırır.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")
            raise ValueError("GEMINI_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")
        
        # Gemini API'yi yapılandır
        logger.debug(f"Gemini API yapılandırılıyor. API anahtarı: {api_key[:5]}...")
        genai.configure(api_key=api_key)
        
        # Gemini modeli
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.debug("Gemini modeli oluşturuldu: gemini-1.5-flash")
    
    def analyze_transcript(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transkripti analiz eder ve öğrenme düzeyini belirler.
        
        Args:
            transcript_data (Dict[str, Any]): İşlenmiş transkript verileri.
            
        Returns:
            Dict[str, Any]: Analiz sonuçları.
        """
        # Tüm konuşma metinlerini al
        all_text = transcript_data.get('all_text', '')
        logger.debug(f"Analiz edilecek metin uzunluğu: {len(all_text)} karakter")
        
        # Metin çok uzunsa, ilk 8000 karakteri al (Gemini API sınırlamaları nedeniyle)
        if len(all_text) > 8000:
            all_text = all_text[:8000]
            logger.debug("Metin çok uzun, ilk 8000 karakter alındı.")
        
        # Yapay zekaya gönderilecek istek
        prompt = f"""
        Aşağıdaki İngilizce ders transkriptini analiz et ve şu bilgileri çıkar:
        
        1. Öğrencinin İngilizce seviyesi (A1, A2, B1, B2, C1, C2)
        2. Öğrencinin güçlü yönleri
        3. Öğrencinin geliştirmesi gereken alanlar
        4. Derste öğrenilen yeni kelimeler ve deyimler
        5. Derste tartışılan ana konular
        
        Transkript:
        {all_text}
        
        Lütfen analiz sonuçlarını JSON formatında döndür.
        """
        
        try:
            # Yapay zekadan yanıt al
            logger.debug("Yapay zekadan analiz yanıtı isteniyor...")
            response = self.model.generate_content(prompt)
            
            # Yanıtı işle
            analysis_text = response.text
            logger.debug(f"Yapay zeka analiz yanıtı alındı. Uzunluk: {len(analysis_text)} karakter")
            
            # Basit bir analiz sonucu oluştur
            analysis_result = {
                'raw_analysis': analysis_text,
                'success': True
            }
            
            return analysis_result
        except Exception as e:
            logger.error(f"Yapay zeka analizi sırasında hata oluştu: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_zoom_transcript(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Zoom transkriptini analiz eder ve konuşanları tespit ederek öğrenme düzeyini belirler.
        
        Args:
            transcript_data (Dict[str, Any]): İşlenmiş transkript verileri.
            
        Returns:
            Dict[str, Any]: Analiz sonuçları.
        """
        # Konuşmacı verilerini al
        speakers = transcript_data.get('speakers', {})
        speaker_counts = transcript_data.get('speaker_counts', {})
        all_text = transcript_data.get('all_text', '')
        
        logger.debug(f"Zoom analizi için konuşmacı sayısı: {len(speakers)}")
        logger.debug(f"Zoom analizi için metin uzunluğu: {len(all_text)} karakter")
        
        # Metin çok uzunsa, ilk 8000 karakteri al
        if len(all_text) > 8000:
            all_text = all_text[:8000]
            logger.debug("Metin çok uzun, ilk 8000 karakter alındı.")
        
        # Konuşmacı bilgilerini hazırla
        speaker_data = []
        for speaker, texts in speakers.items():
            speaker_text = "\n".join(texts[:20])  # Her konuşmacı için en fazla 20 konuşma örneği
            speaker_data.append(f"Konuşmacı: {speaker}\nKonuşma Sayısı: {speaker_counts.get(speaker, 0)}\nKonuşma Örnekleri:\n{speaker_text}\n")
        
        speakers_info = "\n".join(speaker_data)
        
        # Yapay zekaya gönderilecek istek
        prompt = f"""
        Aşağıdaki Zoom ders transkriptini analiz et. Bu transkript, bir eğitmen ile bir öğrenci arasındaki diyaloğu içeriyor.
        
        1. Konuşmacıları analiz ederek hangisinin öğretmen, hangisinin öğrenci olduğunu belirle.
        2. Öğrencinin İngilizce seviyesini tespit et (A1, A2, B1, B2, C1, C2).
        3. Öğrencinin güçlü yönlerini belirle.
        4. Öğrencinin geliştirmesi gereken alanları belirle.
        5. Derste öğrenilen yeni kelimeler ve deyimleri listele.
        6. Derste tartışılan ana konuları özetle.
        
        Konuşmacı Bilgileri:
        {speakers_info}
        
        Transkript:
        {all_text}
        
        Lütfen analiz sonuçlarını JSON formatında döndür. Format şöyle olmalı:
        {{
          "ogretmen": "Konuşmacının adı",
          "ogrenci": "Konuşmacının adı",
          "seviye": "B1", (Öğrencinin tespit edilen seviyesi)
          "guclu_yonler": ["güçlü yön 1", "güçlü yön 2", ...],
          "gelistirilmesi_gerekenler": ["alan 1", "alan 2", ...],
          "yeni_kelimeler": ["kelime 1", "kelime 2", ...],
          "ana_konular": ["konu 1", "konu 2", ...]
        }}
        """
        
        try:
            # Yapay zekadan yanıt al
            logger.debug("Yapay zekadan Zoom analiz yanıtı isteniyor...")
            response = self.model.generate_content(prompt)
            
            # Yanıtı işle
            analysis_text = response.text
            logger.debug(f"Yapay zeka Zoom analiz yanıtı alındı. Uzunluk: {len(analysis_text)} karakter")
            
            # Basit bir analiz sonucu oluştur
            analysis_result = {
                'raw_analysis': analysis_text,
                'success': True
            }
            
            return analysis_result
        except Exception as e:
            logger.error(f"Zoom transkripti analizi sırasında hata oluştu: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_tests(self, analysis_result: Dict[str, Any], transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiz sonuçlarına göre kişiselleştirilmiş testler oluşturur.
        
        Args:
            analysis_result (Dict[str, Any]): Analiz sonuçları.
            transcript_data (Dict[str, Any]): İşlenmiş transkript verileri.
            
        Returns:
            Dict[str, Any]: Oluşturulan testler.
        """
        if not analysis_result.get('success', False):
            logger.error("Analiz sonuçları bulunamadı.")
            return {
                'success': False,
                'error': 'Analiz sonuçları bulunamadı.'
            }
        
        # Analiz sonuçlarını al
        raw_analysis = analysis_result.get('raw_analysis', '')
        logger.debug(f"Test oluşturmak için analiz sonucu uzunluğu: {len(raw_analysis)} karakter")
        
        # Tüm konuşma metinlerini al
        all_text = transcript_data.get('all_text', '')
        logger.debug(f"Test oluşturmak için metin uzunluğu: {len(all_text)} karakter")
        
        # Metin çok uzunsa, ilk 8000 karakteri al
        if len(all_text) > 8000:
            all_text = all_text[:8000]
            logger.debug("Metin çok uzun, ilk 8000 karakter alındı.")
        
        # Yapay zekaya gönderilecek istek
        prompt = f"""
        Aşağıdaki İngilizce ders transkriptini ve analiz sonuçlarını kullanarak, 
        öğrencinin seviyesine uygun 5 adet kısa, interaktif ve eğlenceli ingilizce test sorusu oluştur.
        Sorular öğrencinin eksiklerine yönelik olsun. Soruları atanmış seviyesine göre yap. örneğin B2 seviyesinde örnek sorular. 
        yüklenmiş belgedeki kişisel bilgilerden soru türetme bunun yerine seviyesine ve yeni öğrendiği kelimeler ve hatalarına yönelik sorular üret. Öğrenci için sıfat olarak "Öğrenci" kelimesini kullan "konuşmacı" kelimesini kullanma lütfen
        
        DİKKAT: Öğrencinin seviyesine göre soru dili değişiklik gösterecek:
        - Eğer seviyesi A1 veya A2 ise sorular Türkçe, cevap seçenekleri İngilizce olacak
        - Eğer seviyesi B1, B2, C1 veya C2 ise hem sorular hem de cevap seçenekleri İngilizce olacak
        
        Her soru şunları içermeli:
        1. Soru metni
        2. 4 seçenek (A, B, C, D)
        3. Doğru cevap
        4. Kısa bir açıklama
        
        Sorular şu türlerde olabilir:
        - Kelime bilgisi
        - Dilbilgisi
        - Dinleme anlama
        - Okuma anlama
        - Deyimler ve kalıplar
        
        Transkript:
        {all_text}
        
        Analiz Sonuçları:
        {raw_analysis}
        
        Lütfen test sorularını JSON formatında döndür. Aşağıdaki formatta olmalıdır:
        
        ```
        [
          {{
            "question": "Soru metni",
            "options": [
              {{"letter": "A", "text": "Seçenek A"}},
              {{"letter": "B", "text": "Seçenek B"}},
              {{"letter": "C", "text": "Seçenek C"}},
              {{"letter": "D", "text": "Seçenek D"}}
            ],
            "correct_answer": "A",
            "explanation": "Açıklama"
          }}
        ]
        ```
        """
        
        try:
            # Yapay zekadan yanıt al
            logger.debug("Yapay zekadan test yanıtı isteniyor...")
            response = self.model.generate_content(prompt)
            
            # Yanıtı işle
            tests_text = response.text
            logger.debug(f"Yapay zeka test yanıtı alındı. Uzunluk: {len(tests_text)} karakter")
            logger.debug(f"Test yanıtı: {tests_text[:200]}...")
            
            # API yanıtı boş veya geçersizse örnek test verileri kullan
            if not tests_text or "```" not in tests_text:
                logger.warning("Geçerli test yanıtı alınamadı, örnek test verileri kullanılıyor.")
                tests_text = self._get_sample_tests()
            
            # Test sonuçlarını döndür
            return {
                'raw_tests': tests_text,
                'success': True
            }
        except Exception as e:
            logger.error(f"Test oluşturma sırasında hata oluştu: {str(e)}")
            # Hata durumunda örnek test verileri kullan
            logger.warning("Hata nedeniyle örnek test verileri kullanılıyor.")
            return {
                'raw_tests': self._get_sample_tests(),
                'success': True
            }

    def generate_zoom_tests(self, analysis_result: Dict[str, Any], transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Zoom transkript analiz sonuçlarına göre kişiselleştirilmiş testler oluşturur.
        
        Args:
            analysis_result (Dict[str, Any]): Analiz sonuçları.
            transcript_data (Dict[str, Any]): İşlenmiş transkript verileri.
            
        Returns:
            Dict[str, Any]: Oluşturulan testler.
        """
        if not analysis_result.get('success', False):
            logger.error("Analiz sonuçları bulunamadı.")
            return {
                'success': False,
                'error': 'Analiz sonuçları bulunamadı.'
            }
        
        # Analiz sonuçlarını al
        raw_analysis = analysis_result.get('raw_analysis', '')
        logger.debug(f"Zoom testi oluşturmak için analiz sonucu uzunluğu: {len(raw_analysis)} karakter")
        
        # Tüm konuşma metinlerini al
        all_text = transcript_data.get('all_text', '')
        logger.debug(f"Zoom testi oluşturmak için metin uzunluğu: {len(all_text)} karakter")
        
        # Metin çok uzunsa, ilk 8000 karakteri al
        if len(all_text) > 8000:
            all_text = all_text[:8000]
            logger.debug("Metin çok uzun, ilk 8000 karakter alındı.")
        
        # Yapay zekaya gönderilecek istek
        prompt = f"""
        Aşağıdaki Zoom ders transkriptini ve analiz sonuçlarını kullanarak, 
        öğrencinin seviyesine uygun 5 adet kısa, interaktif ve eğlenceli test sorusu oluştur.
        
        Test soruları, öğrencinin analiz edilen seviyesine ve geliştirmesi gereken alanlara odaklanmalıdır.
        
        DİKKAT: Öğrencinin seviyesine göre soru dili değişiklik gösterecek:
        - Eğer seviyesi A1 veya A2 ise sorular Türkçe, cevap seçenekleri İngilizce olacak
        - Eğer seviyesi B1, B2, C1 veya C2 ise hem sorular hem de cevap seçenekleri İngilizce olacak
        
        Her soru şunları içermeli:
        1. Soru metni
        2. 4 seçenek (A, B, C, D)
        3. Doğru cevap
        4. Kısa bir açıklama
        
        Sorular şu türlerde olabilir:
        - Kelime bilgisi
        - Dilbilgisi
        - Dinleme anlama
        - Okuma anlama
        - Deyimler ve kalıplar
        
        Transkript:
        {all_text}
        
        Analiz Sonuçları:
        {raw_analysis}
        
        Lütfen test sorularını JSON formatında döndür. Aşağıdaki formatta olmalıdır:
        
        ```
        [
          {{
            "question": "Soru metni",
            "options": [
              {{"letter": "A", "text": "Seçenek A"}},
              {{"letter": "B", "text": "Seçenek B"}},
              {{"letter": "C", "text": "Seçenek C"}},
              {{"letter": "D", "text": "Seçenek D"}}
            ],
            "correct_answer": "A",
            "explanation": "Açıklama"
          }}
        ]
        ```
        """
        
        try:
            # Yapay zekadan yanıt al
            logger.debug("Yapay zekadan Zoom test yanıtı isteniyor...")
            response = self.model.generate_content(prompt)
            
            # Yanıtı işle
            tests_text = response.text
            logger.debug(f"Yapay zeka Zoom test yanıtı alındı. Uzunluk: {len(tests_text)} karakter")
            
            # API yanıtı boş veya geçersizse örnek test verileri kullan
            if not tests_text or "```" not in tests_text:
                logger.warning("Geçerli Zoom test yanıtı alınamadı, örnek test verileri kullanılıyor.")
                tests_text = self._get_sample_tests()
            
            # Test sonuçlarını döndür
            return {
                'raw_tests': tests_text,
                'success': True
            }
        except Exception as e:
            logger.error(f"Zoom test oluşturma sırasında hata oluştu: {str(e)}")
            # Hata durumunda örnek test verileri kullan
            logger.warning("Hata nedeniyle örnek Zoom test verileri kullanılıyor.")
            return {
                'raw_tests': self._get_sample_tests(),
                'success': True
            }

    def _get_sample_tests(self) -> str:
        """
        Örnek test verileri döndürür.
        
        Returns:
            str: Örnek test verileri.
        """
        logger.debug("Örnek test verileri oluşturuluyor.")
        return """```
[
  {
    "question": "What is the meaning of 'to get the hang of something'?",
    "options": [
      {"letter": "A", "text": "To hang something on the wall"},
      {"letter": "B", "text": "To understand how to do something"},
      {"letter": "C", "text": "To give up on something"},
      {"letter": "D", "text": "To forget about something"}
    ],
    "correct_answer": "B",
    "explanation": "The phrase 'to get the hang of something' means to understand how to do something or to become skilled at something through practice."
  },
  {
    "question": "Which of the following is the correct past tense form of the verb 'speak'?",
    "options": [
      {"letter": "A", "text": "Speaked"},
      {"letter": "B", "text": "Spoke"},
      {"letter": "C", "text": "Speaking"},
      {"letter": "D", "text": "Speaken"}
    ],
    "correct_answer": "B",
    "explanation": "The correct past tense form of 'speak' is 'spoke'. It is an irregular verb."
  },
  {
    "question": "What does the idiom 'it's raining cats and dogs' mean?",
    "options": [
      {"letter": "A", "text": "It's raining animals"},
      {"letter": "B", "text": "It's a light rain"},
      {"letter": "C", "text": "It's raining very heavily"},
      {"letter": "D", "text": "It's a sunny day"}
    ],
    "correct_answer": "C",
    "explanation": "The idiom 'it's raining cats and dogs' means it's raining very heavily or it's a downpour."
  },
  {
    "question": "Choose the correct word to complete the sentence: 'She _____ to the store yesterday.'",
    "options": [
      {"letter": "A", "text": "go"},
      {"letter": "B", "text": "goes"},
      {"letter": "C", "text": "went"},
      {"letter": "D", "text": "going"}
    ],
    "correct_answer": "C",
    "explanation": "The correct word is 'went', which is the past tense of 'go'. The sentence is in the past tense as indicated by 'yesterday'."
  }
]
```""" 