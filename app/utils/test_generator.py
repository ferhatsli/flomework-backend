import json
import logging
import random
from typing import Dict, List, Any

# Loglama yapılandırması
logger = logging.getLogger(__name__)

class TestGenerator:
    """
    Transkript verisinden test soruları üreten sınıf.
    """
    
    def __init__(self, transcript_data: Dict[str, Any]):
        """
        TestGenerator sınıfını başlatır.
        
        Args:
            transcript_data (Dict[str, Any]): İşlenmiş transkript verisi
        """
        self.transcript_data = transcript_data
        self.openai_data = transcript_data.get('openai', {})
        self.gladia_data = transcript_data.get('gladia_response', [])
        self.calculations = transcript_data.get('calculations', {})
        
    def generate_multiple_choice(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Çoktan seçmeli sorular üretir.
        
        Args:
            count (int): Üretilecek soru sayısı
            
        Returns:
            List[Dict[str, Any]]: Üretilen sorular
        """
        questions = []
        topics = self._extract_topics()
        
        for _ in range(count):
            topic = random.choice(topics)
            question = self._create_multiple_choice_question(topic)
            if question:
                questions.append(question)
                
        return questions[:count]  # İstenen sayıda soru döndür
    
    def generate_true_false(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Doğru/Yanlış soruları üretir.
        
        Args:
            count (int): Üretilecek soru sayısı
            
        Returns:
            List[Dict[str, Any]]: Üretilen sorular
        """
        questions = []
        statements = self._extract_statements()
        
        for _ in range(count):
            statement = random.choice(statements)
            question = self._create_true_false_question(statement)
            if question:
                questions.append(question)
                
        return questions[:count]
    
    def generate_fill_in_blanks(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Boşluk doldurma soruları üretir.
        
        Args:
            count (int): Üretilecek soru sayısı
            
        Returns:
            List[Dict[str, Any]]: Üretilen sorular
        """
        questions = []
        sentences = self._extract_sentences()
        
        for _ in range(count):
            sentence = random.choice(sentences)
            question = self._create_fill_in_blank_question(sentence)
            if question:
                questions.append(question)
                
        return questions[:count]
    
    def _extract_topics(self) -> List[str]:
        """
        Transkript verisinden konu başlıklarını çıkarır.
        """
        topics = []
        
        # OpenAI analizinden konuları çıkar
        if 'topics' in self.openai_data:
            topics.extend(self.openai_data['topics'])
            
        # Gladia verisinden konuları çıkar
        for utterance in self.gladia_data:
            if 'topic' in utterance:
                topics.append(utterance['topic'])
                
        return list(set(topics))  # Tekrar edenleri kaldır
    
    def _extract_statements(self) -> List[str]:
        """
        Transkript verisinden ifadeleri çıkarır.
        """
        statements = []
        
        # Gladia verisinden ifadeleri çıkar
        for utterance in self.gladia_data:
            if 'text' in utterance:
                statements.append(utterance['text'])
                
        return statements
    
    def _extract_sentences(self) -> List[str]:
        """
        Transkript verisinden cümleleri çıkarır.
        """
        sentences = []
        
        # Gladia verisinden cümleleri çıkar
        for utterance in self.gladia_data:
            if 'text' in utterance:
                # Basit cümle ayırma
                text_sentences = utterance['text'].split('.')
                sentences.extend([s.strip() for s in text_sentences if s.strip()])
                
        return sentences
    
    def _create_multiple_choice_question(self, topic: str) -> Dict[str, Any]:
        """
        Verilen konuyla ilgili çoktan seçmeli soru oluşturur.
        """
        # Konu ile ilgili metni bul
        relevant_text = self._find_relevant_text(topic)
        
        if not relevant_text:
            return None
            
        # Soru oluştur
        return {
            'type': 'multiple_choice',
            'question': f"What is the main point discussed about {topic}?",
            'options': [
                {'id': 'A', 'text': relevant_text},
                {'id': 'B', 'text': "This is an incorrect option"},
                {'id': 'C', 'text': "This is another incorrect option"},
                {'id': 'D', 'text': "This is the last incorrect option"}
            ],
            'correct_answer': 'A',
            'explanation': f"The correct answer explains the main point about {topic}."
        }
    
    def _create_true_false_question(self, statement: str) -> Dict[str, Any]:
        """
        Verilen ifadeden doğru/yanlış sorusu oluşturur.
        """
        return {
            'type': 'true_false',
            'question': statement,
            'options': [
                {'id': 'T', 'text': 'True'},
                {'id': 'F', 'text': 'False'}
            ],
            'correct_answer': 'T',
            'explanation': "This statement is true based on the conversation."
        }
    
    def _create_fill_in_blank_question(self, sentence: str) -> Dict[str, Any]:
        """
        Verilen cümleden boşluk doldurma sorusu oluşturur.
        """
        # Cümleden bir kelime seç
        words = sentence.split()
        if len(words) < 3:  # Çok kısa cümleler için
            return None
            
        word_to_blank = random.choice(words[1:-1])  # İlk ve son kelimeyi seçme
        blank_sentence = sentence.replace(word_to_blank, "_____")
        
        return {
            'type': 'fill_in_blank',
            'question': blank_sentence,
            'correct_answer': word_to_blank,
            'explanation': f"The word '{word_to_blank}' completes the sentence correctly."
        }
    
    def _find_relevant_text(self, topic: str) -> str:
        """
        Verilen konuyla ilgili metni bulur.
        """
        for utterance in self.gladia_data:
            if topic.lower() in utterance.get('text', '').lower():
                return utterance['text']
        return ""

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

    def get_tests_as_json(self) -> List[Dict[str, Any]]:
        """
        Test verilerini JSON formatında döndürür.
        Her zaman en fazla 10 soru döndürür.
        
        Returns:
            List[Dict[str, Any]]: İşlenmiş test verileri (maksimum 10 soru).
        """
        if not self.processed_tests:
            return []
            
        # En fazla 10 soru döndür
        return self.processed_tests[:10] 