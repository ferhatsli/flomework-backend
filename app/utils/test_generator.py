import json
import logging
from typing import Dict, List, Any

# Loglama yapılandırması
logger = logging.getLogger(__name__)

class TestGenerator:
    """
    Yapay zeka tarafından oluşturulan test verilerini işler ve kullanılabilir formata dönüştürür.
    """
    
    def __init__(self, raw_tests: str):
        """
        TestGenerator sınıfını başlatır.
        
        Args:
            raw_tests (str): Yapay zeka tarafından oluşturulan ham test verileri.
        """
        self.raw_tests = raw_tests
        self.processed_tests = None
        logger.debug(f"Ham test verileri: {raw_tests}")
    
    def process_tests(self) -> List[Dict[str, Any]]:
        """
        Ham test verilerini işler ve yapılandırılmış bir formata dönüştürür.
        
        Returns:
            List[Dict[str, Any]]: İşlenmiş test verileri.
        """
        try:
            # JSON formatındaki metni ayrıştır
            # Not: Yapay zeka çıktısı her zaman düzgün JSON olmayabilir
            # Bu nedenle, JSON ayrıştırma hatası durumunda manuel ayrıştırma yapılır
            try:
                # JSON formatını temizle (yapay zeka bazen kod bloğu içinde JSON döndürebilir)
                cleaned_json = self._clean_json_string(self.raw_tests)
                logger.debug(f"Temizlenmiş JSON: {cleaned_json}")
                tests_data = json.loads(cleaned_json)
                logger.debug(f"JSON yüklendi: {tests_data}")
                
                # JSON yapısına göre işleme
                if isinstance(tests_data, list):
                    self.processed_tests = tests_data
                    logger.debug("Liste formatında testler işlendi.")
                elif isinstance(tests_data, dict) and 'questions' in tests_data:
                    self.processed_tests = tests_data['questions']
                    logger.debug("Sözlük formatında testler işlendi (questions anahtarı).")
                else:
                    # Diğer JSON yapıları için
                    self.processed_tests = [tests_data]
                    logger.debug("Diğer JSON formatında testler işlendi.")
            except json.JSONDecodeError as e:
                # Manuel ayrıştırma
                logger.debug(f"JSON ayrıştırma hatası: {str(e)}. Manuel ayrıştırma yapılıyor.")
                self.processed_tests = self._manually_parse_tests()
            
            # Test verilerini doğrula ve temizle
            self._validate_and_clean_tests()
            
            return self.processed_tests
        except Exception as e:
            logger.error(f"Test verileri işlenirken hata oluştu: {str(e)}")
            return []
    
    def _clean_json_string(self, json_str: str) -> str:
        """
        JSON dizesini temizler ve geçerli bir JSON formatına dönüştürür.
        
        Args:
            json_str (str): Temizlenecek JSON dizesi.
            
        Returns:
            str: Temizlenmiş JSON dizesi.
        """
        if not json_str:
            logger.warning("Boş JSON dizesi.")
            return "{}"
            
        # Kod bloklarını temizle
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
            logger.debug("```json kod bloğu temizlendi.")
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
            logger.debug("``` kod bloğu temizlendi.")
        
        return json_str
    
    def _manually_parse_tests(self) -> List[Dict[str, Any]]:
        """
        Ham test verilerini manuel olarak ayrıştırır.
        
        Returns:
            List[Dict[str, Any]]: Manuel olarak ayrıştırılmış test verileri.
        """
        # Basit bir manuel ayrıştırma
        tests = []
        lines = self.raw_tests.split('\n')
        logger.debug(f"Manuel ayrıştırma için {len(lines)} satır.")
        
        current_test = {}
        for line in lines:
            line = line.strip()
            
            # Yeni soru başlangıcı
            if line.startswith("Soru ") or line.startswith("Question "):
                if current_test and 'question' in current_test:
                    tests.append(current_test)
                    logger.debug(f"Yeni test eklendi: {current_test}")
                current_test = {'question': line, 'options': []}
                logger.debug(f"Yeni soru başladı: {line}")
            
            # Seçenekler
            elif line.startswith(("A)", "B)", "C)", "D)")):
                option_letter = line[0]
                option_text = line[2:].strip()
                current_test.setdefault('options', []).append({
                    'letter': option_letter,
                    'text': option_text
                })
                logger.debug(f"Seçenek eklendi: {option_letter} - {option_text}")
            
            # Doğru cevap
            elif "Doğru cevap:" in line or "Correct answer:" in line:
                current_test['correct_answer'] = line.split(":")[-1].strip()
                logger.debug(f"Doğru cevap eklendi: {current_test['correct_answer']}")
            
            # Açıklama
            elif "Açıklama:" in line or "Explanation:" in line:
                current_test['explanation'] = line.split(":")[-1].strip()
                logger.debug(f"Açıklama eklendi: {current_test['explanation']}")
        
        # Son soruyu ekle
        if current_test and 'question' in current_test:
            tests.append(current_test)
            logger.debug(f"Son test eklendi: {current_test}")
        
        logger.debug(f"Manuel ayrıştırma sonucu {len(tests)} test oluşturuldu.")
        return tests
    
    def _validate_and_clean_tests(self) -> None:
        """
        Test verilerini doğrular ve temizler.
        """
        if not self.processed_tests:
            logger.warning("İşlenecek test verisi yok.")
            return
        
        cleaned_tests = []
        for test in self.processed_tests:
            # Gerekli alanları kontrol et
            if not all(key in test for key in ['question']):
                logger.warning(f"Geçersiz test: 'question' alanı eksik - {test}")
                continue
            
            # Seçenekleri kontrol et
            if 'options' not in test or not test['options']:
                logger.debug(f"Test için seçenekler oluşturuluyor: {test['question']}")
                # Seçenekleri A, B, C, D anahtarlarından oluştur
                options = []
                for letter in ['A', 'B', 'C', 'D']:
                    if letter in test:
                        options.append({
                            'letter': letter,
                            'text': test[letter]
                        })
                test['options'] = options
            
            # Doğru cevabı kontrol et
            if 'correct_answer' not in test:
                if 'answer' in test:
                    test['correct_answer'] = test['answer']
                    logger.debug(f"Doğru cevap 'answer' alanından alındı: {test['correct_answer']}")
                else:
                    # Varsayılan olarak A'yı seç
                    test['correct_answer'] = 'A'
                    logger.warning(f"Doğru cevap bulunamadı, varsayılan olarak 'A' seçildi: {test['question']}")
            
            # Açıklamayı kontrol et
            if 'explanation' not in test:
                test['explanation'] = "Açıklama bulunmuyor."
                logger.debug(f"Açıklama bulunamadı, varsayılan açıklama eklendi: {test['question']}")
            
            cleaned_tests.append(test)
        
        logger.debug(f"Temizleme sonrası {len(cleaned_tests)} test kaldı.")
        self.processed_tests = cleaned_tests
    
    def get_tests_as_html(self) -> str:
        """
        Test verilerini HTML formatında döndürür.
        
        Returns:
            str: HTML formatında test verileri.
        """
        if not self.processed_tests:
            logger.warning("HTML oluşturmak için test verisi yok.")
            return "<p>Test verileri bulunamadı.</p>"
        
        html = "<div class='tests-container'>"
        
        for i, test in enumerate(self.processed_tests, 1):
            html += f"<div class='test-item' id='test-{i}'>"
            html += f"<h3 class='question'>{i}. {test['question']}</h3>"
            html += "<div class='options'>"
            
            for option in test.get('options', []):
                letter = option.get('letter', '')
                text = option.get('text', '')
                html += f"""
                <div class='option'>
                    <input type='radio' name='test-{i}' id='test-{i}-{letter}' value='{letter}'>
                    <label for='test-{i}-{letter}'>{letter}) {text}</label>
                </div>
                """
            
            html += "</div>"
            html += f"<div class='explanation' style='display:none;'>{test.get('explanation', '')}</div>"
            html += f"<div class='correct-answer' data-answer='{test.get('correct_answer', '')}'></div>"
            html += "<button class='check-answer-btn'>Cevabı Kontrol Et</button>"
            html += "</div>"
        
        html += "</div>"
        logger.debug(f"{len(self.processed_tests)} test için HTML oluşturuldu.")
        return html 