import requests
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class FlalingoError(Exception):
    """Özel hata sınıfı"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

ERROR_CODES = {
    'AUTH_ERROR': 'Authentication failed',
    'REPORT_NOT_FOUND': 'Flai report not found',
    'SERVICE_ERROR': 'Service temporarily unavailable',
    'QUESTION_GEN_ERROR': 'Failed to generate questions',
    'EVALUATION_ERROR': 'Failed to evaluate answers'
}

class FlalingoService:
    """
    Flalingo API ile iletişim kuran servis sınıfı.
    """
    
    def __init__(self):
        """
        FlalingoService sınıfını başlatır.
        """
        self.base_url = "https://exercise.flalingo.com/api"
        
    def get_transcript(self, auth_token: str, flai_report: str) -> Dict[str, Any]:
        """
        Gladia'dan transkript verisini alır ve soru üretimi yapar.
        
        Args:
            auth_token (str): API token
            flai_report (str): Flai report ID
            
        Returns:
            Dict[str, Any]: Üretilen sorular ve metadata
            
        Raises:
            FlalingoError: API isteği başarısız olduğunda
        """
        try:
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            # Gladia'dan transkript verisi al
            response = requests.get(
                f"{self.base_url}/flai-transcript",
                params={
                    'auth_token': auth_token,
                    'flai_report': flai_report
                },
                headers=headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success'):
                raise FlalingoError('SERVICE_ERROR', data.get('error', 'Failed to get transcript'))
            
            # Soru üretimi için veriyi hazırla
            transcript_data = {
                'openai': data.get('data', {}).get('openai', {}),
                'gladia_response': data.get('data', {}).get('gladia_response', []),
                'calculations': data.get('data', {}).get('calculations', {})
            }
            
            # Soru üretimi yap
            questions = self._generate_questions(transcript_data)
            
            return {
                'success': True,
                'data': {
                    'questions': questions
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API isteği sırasında hata: {str(e)}")
            raise FlalingoError('SERVICE_ERROR', str(e))

    def _generate_questions(self, transcript_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Transkript verisinden soru üretimi yapar.
        
        Args:
            transcript_data: Transkript verisi
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Üretilen sorular
        """
        try:
            # Test generator'ı kullanarak soruları üret
            from .test_generator import TestGenerator
            generator = TestGenerator(transcript_data)
            
            return {
                'multiple_choice': generator.generate_multiple_choice(10),
                'true_false': generator.generate_true_false(5),
                'fill_in_blanks': generator.generate_fill_in_blanks(5)
            }
            
        except Exception as e:
            logger.error(f"Soru üretimi sırasında hata: {str(e)}")
            raise FlalingoError('QUESTION_GEN_ERROR', str(e))

    def send_exercise_completion(self, auth_token: str, flai_report: str, 
                               exercise_response: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Test sonuçlarını değerlendirir.
        
        Args:
            auth_token (str): API token
            flai_report (str): Flai report ID
            exercise_response (Dict): Kullanıcı cevapları
            
        Returns:
            Dict[str, Any]: Değerlendirme sonuçları
        """
        try:
            # Sonuçları değerlendir
            results = self._evaluate_results(exercise_response)
            
            return {
                'success': True,
                'data': results
            }
            
        except Exception as e:
            logger.error(f"Sonuç değerlendirme sırasında hata: {str(e)}")
            raise FlalingoError('EVALUATION_ERROR', str(e))

    def _evaluate_results(self, exercise_response: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Test sonuçlarını değerlendirir ve istatistikleri hesaplar.
        
        Args:
            exercise_response: Kullanıcı cevapları
            
        Returns:
            Dict[str, Any]: Değerlendirme sonuçları
        """
        total_correct = 0
        total_questions = 0
        by_type = {}
        
        for q_type, answers in exercise_response.items():
            correct = sum(1 for a in answers if a['user_answer'] == a['correct_answer'])
            total = len(answers)
            
            by_type[q_type] = {
                'correct': correct,
                'wrong': total - correct,
                'success_rate': (correct / total * 100) if total > 0 else 0
            }
            
            total_correct += correct
            total_questions += total
        
        return {
            'summary': {
                'total_questions': total_questions,
                'correct_answers': total_correct,
                'wrong_answers': total_questions - total_correct,
                'success_rate': (total_correct / total_questions * 100) if total_questions > 0 else 0
            },
            'by_question_type': by_type
        } 