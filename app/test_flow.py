from utils.flalingo_service import FlalingoService
from utils.transcript_processor import TranscriptProcessor
from utils.ai_analyzer import AIAnalyzer
from utils.mock_data import (
    MOCK_FRONTEND_REQUEST,
    MOCK_GLADIA_RESPONSE,
    MOCK_USER_ANSWERS,
    MOCK_QUESTIONS  # Test için örnek soruları ekledik
)
import json

def generate_test_answers(questions):
    test_answers = {
        "multiple_choice": [],
        "true_false": [],
        "fill_in_blank": []
    }
    
    # Çoktan seçmeli sorular için
    for idx, question in enumerate(questions["multiple_choice"]):
        test_answers["multiple_choice"].append({
            "question_id": idx,
            "user_answer": question["correct_answer"]
        })
    
    # Doğru/Yanlış soruları için
    for idx, question in enumerate(questions["true_false"]):
        test_answers["true_false"].append({
            "question_id": idx,
            "user_answer": question["correct_answer"]
        })
    
    # Boşluk doldurma soruları için
    for idx, question in enumerate(questions["fill_in_blank"]):
        test_answers["fill_in_blank"].append({
            "question_id": idx,
            "user_answer": question["correct_answer"]
        })
    
    return test_answers

def modify_some_answers(test_answers):
    """Gerçekçi test için bazı cevapları yanlış yapar"""
    if test_answers["multiple_choice"]:
        # İlk çoktan seçmeli soruyu yanlış yapalım
        test_answers["multiple_choice"][0]["user_answer"] = "B"
    
    if test_answers["true_false"]:
        # İlk doğru/yanlış sorusunu yanlış yapalım
        current = test_answers["true_false"][0]["user_answer"]
        test_answers["true_false"][0]["user_answer"] = "F" if current == "T" else "T"
    
    if test_answers["fill_in_blank"]:
        # İlk boşluk doldurma sorusunu yanlış yapalım
        test_answers["fill_in_blank"][0]["user_answer"] = "wrong_answer"
    
    return test_answers

def main():
    print("\n=== Test Başlıyor ===\n")

    # 1. Frontend'den gelen istek
    frontend_request = {
        "api_token": "test_token_123",
        "flai_report": "report_123"
    }
    print("1. Frontend'den istek alındı:")
    print(json.dumps(frontend_request, indent=2))

    # 2. Gladia'dan yanıt
    print("\n2. Gladia'dan yanıt alındı:")
    print(f"Konuşma sayısı: {len(MOCK_GLADIA_RESPONSE['gladia_response'])}")

    # 3. Transkript işleme
    print("\n3. Transkript işleniyor...")
    processor = TranscriptProcessor(MOCK_GLADIA_RESPONSE)
    processed_data = processor.process_transcript()
    print("İşleme tamamlandı.")
    print("Hesaplanan istatistikler:")
    print(json.dumps(processed_data, indent=2))

    # 4. AI Analizi ve Soru Üretimi
    print("\n4. AI Analizi ve Soru Üretimi başlıyor...\n")
    analyzer = AIAnalyzer()
    
    print("Transkript analiz ediliyor...")
    analysis = analyzer.analyze_transcript(processed_data)
    print("Analiz tamamlandı:")
    print(json.dumps(analysis, indent=2))

    print("\nSorular üretiliyor...")
    questions = analyzer.generate_questions(processed_data)
    
    if questions.get('success'):
        print("Soru üretimi tamamlandı.")
        print("Üretilen soru sayısı:")
        print(f"- Çoktan seçmeli: {len(questions['questions']['multiple_choice'])}")
        print(f"- Doğru/Yanlış: {len(questions['questions']['true_false'])}")
        print(f"- Boşluk doldurma: {len(questions['questions']['fill_in_blank'])}")
        
        print("\nÜretilen sorular:")
        print(json.dumps(questions['questions'], indent=2))

        # 5. Test cevapları oluştur
        print("\n5. Test cevapları oluşturuluyor...")
        test_answers = generate_test_answers(questions['questions'])
        
        # Bazı cevapları yanlış yap
        test_answers = modify_some_answers(test_answers)
        
        print("Oluşturulan test cevapları:")
        print(json.dumps(test_answers, indent=2))

        # 6. Cevapları değerlendir
        print("\n6. Cevaplar değerlendiriliyor...")
        evaluation = analyzer.evaluate_answers(questions['questions'], test_answers)
        print("Değerlendirme sonuçları:")
        print(json.dumps(evaluation, indent=2))
    else:
        print("Soru üretimi başarısız oldu!")

    print("\n=== Test Tamamlandı ===\n")

if __name__ == "__main__":
    main() 