import unittest
import os
from app.utils.transcript_processor import TranscriptProcessor
from app.utils.test_generator import TestGenerator

class TestTranscriptProcessor(unittest.TestCase):
    """
    TranscriptProcessor sınıfını test eden birim testleri.
    """
    
    def setUp(self):
        """
        Test öncesi hazırlık.
        """
        self.test_file_path = "flai_reports.csv"
    
    def test_load_transcript(self):
        """
        Transkript yükleme işlevini test eder.
        """
        processor = TranscriptProcessor(self.test_file_path)
        result = processor.load_transcript()
        self.assertTrue(result, "Transkript yükleme başarısız oldu.")
        self.assertIsNotNone(processor.transcript_data, "Transkript verisi boş.")
    
    def test_process_transcript(self):
        """
        Transkript işleme işlevini test eder.
        """
        processor = TranscriptProcessor(self.test_file_path)
        processor.load_transcript()
        processed_data = processor.process_transcript()
        
        self.assertIsNotNone(processed_data, "İşlenmiş veri boş.")
        self.assertIn('speakers', processed_data, "Konuşmacılar bulunamadı.")
        self.assertIn('all_text', processed_data, "Tüm metin bulunamadı.")

class TestTestGenerator(unittest.TestCase):
    """
    TestGenerator sınıfını test eden birim testleri.
    """
    
    def setUp(self):
        """
        Test öncesi hazırlık.
        """
        self.sample_tests = """
        {
            "questions": [
                {
                    "question": "What is the meaning of 'nettle' in Greek?",
                    "options": [
                        {"letter": "A", "text": "Fire"},
                        {"letter": "B", "text": "Water"},
                        {"letter": "C", "text": "Earth"},
                        {"letter": "D", "text": "Air"}
                    ],
                    "correct_answer": "B",
                    "explanation": "According to the transcript, 'nettle' (or 'nero') means 'water' in Greek."
                }
            ]
        }
        """
    
    def test_process_tests(self):
        """
        Test işleme işlevini test eder.
        """
        generator = TestGenerator(self.sample_tests)
        processed_tests = generator.process_tests()
        
        self.assertIsNotNone(processed_tests, "İşlenmiş testler boş.")
        self.assertEqual(len(processed_tests), 1, "Test sayısı yanlış.")
        self.assertEqual(processed_tests[0]['correct_answer'], "B", "Doğru cevap yanlış.")
    
    def test_get_tests_as_html(self):
        """
        HTML formatında test oluşturma işlevini test eder.
        """
        generator = TestGenerator(self.sample_tests)
        generator.process_tests()
        html = generator.get_tests_as_html()
        
        self.assertIsNotNone(html, "HTML çıktısı boş.")
        self.assertIn("What is the meaning of 'nettle' in Greek?", html, "Soru metni HTML'de bulunamadı.")
        self.assertIn("Water", html, "Seçenek metni HTML'de bulunamadı.")

if __name__ == '__main__':
    unittest.main() 