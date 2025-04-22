# app paketi başlatma dosyası
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import os
import json
import logging
import traceback
from app.utils.transcript_processor import TranscriptProcessor
from app.utils.ai_analyzer import AIAnalyzer
from app.utils.test_generator import TestGenerator
from app.utils.flalingo_service import FlalingoService
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Loglama yapılandırması
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Flask uygulamasını oluştur
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://exercise.flalingo.com"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/')
def index():
    """API root - provides API information and available endpoints."""
    return jsonify({
        'name': 'Flalingo API',
        'version': '1.0',
        'description': 'API for analyzing transcripts and generating language learning tests',
        'endpoints': {
            'GET /': 'This information',
            'GET /api/health': 'Health check endpoint',
            'POST /api/upload': 'Upload and process transcript file'
        },
        'documentation': {
            'upload_endpoint': {
                'url': '/api/upload',
                'method': 'POST',
                'content_type': 'multipart/form-data',
                'parameters': {
                    'transcript_file': 'File (txt or csv)'
                },
                'responses': {
                    'success': {
                        'status': 200,
                        'body': {
                            'success': True,
                            'data': {
                                'analysis': 'Analysis result',
                                'tests': 'Generated tests',
                                'file_type': 'txt or csv'
                            }
                        }
                    },
                    'error': {
                        'status': '400/500',
                        'body': {
                            'success': False,
                            'error': 'Error message'
                        }
                    }
                }
            }
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })

@app.route('/api/upload', methods=['POST'])
def upload_transcript():
    """Handle transcript file upload and processing."""
    try:
        if 'transcript_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file found in request'
            }), 400
        
        file = request.files['transcript_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Dosyayı geçici olarak kaydet
        temp_file_path = os.path.join('temp', file.filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_file_path)
        
        # Transkripti işle
        processor = TranscriptProcessor(temp_file_path)
        if not processor.load_transcript():
            return jsonify({
                'success': False,
                'error': 'Failed to load transcript'
            }), 400
        
        processed_data = processor.process_transcript()
        
        # Dosya uzantısına göre analiz metodu belirleme
        analyzer = AIAnalyzer()
        
        if temp_file_path.endswith('.txt'):
            # Text dosyası için Zoom analizi yap
            analysis_result = analyzer.analyze_zoom_transcript(processed_data)
            
            if not analysis_result.get('success', False):
                return jsonify({
                    'success': False,
                    'error': 'Zoom transcript analysis failed'
                }), 500
            
            # Zoom testleri oluştur
            tests_result = analyzer.generate_zoom_tests(analysis_result, processed_data)
        else:
            # CSV dosyası için normal analiz yap
            analysis_result = analyzer.analyze_transcript(processed_data)
            
            if not analysis_result.get('success', False):
                return jsonify({
                    'success': False,
                    'error': 'Transcript analysis failed'
                }), 500
            
            # Test oluştur
            logger.debug("Testler oluşturuluyor...")
            tests_result = analyzer.generate_tests(analysis_result, processed_data)
        
        logger.debug(f"Test sonucu: {tests_result}")
        
        if not tests_result.get('success', False):
            return jsonify({
                'success': False,
                'error': 'Test generation failed'
            }), 500
        
        # Test verilerini işle
        test_generator = TestGenerator(tests_result.get('raw_tests', ''))
        test_generator.process_tests()  # Önce process_tests çağrılmalı
        processed_tests = test_generator.get_tests_as_json()  # Sonra JSON alınmalı
        logger.debug(f"İşlenmiş testler (JSON): {processed_tests}")
        
        # Return results
        return jsonify({
            'success': True,
            'data': {
                'analysis': analysis_result.get('raw_analysis', ''),
                'tests': processed_tests,
                'file_type': 'txt' if temp_file_path.endswith('.txt') else 'csv'
            }
        })
    except Exception as e:
        # Hata detaylarını logla
        logger.error(f"Error during upload process: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Hata mesajını JSON olarak döndür
        return jsonify({
            'success': False,
            'error': f'Processing error: {str(e)}'
        }), 500
    finally:
        # Cleanup temporary file
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.error(f"Error removing temporary file: {str(e)}")

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'message': str(error)
    }), 400

@app.route('/your-custom-exercise')
def custom_exercise():
    """
    Frontend'den gelen ilk istek için yönlendirme endpoint'i.
    """
    auth_token = request.args.get('auth_token')
    flai_report = request.args.get('flai_report')
    
    if not auth_token or not flai_report:
        return jsonify({
            'success': False,
            'error': 'auth_token ve flai_report parametreleri gerekli'
        }), 400
    
    # Frontend'e yönlendir
    return redirect(f'/api/flai-exercise?auth_token={auth_token}&flai_report={flai_report}')

@app.route('/api/flai-exercise', methods=['GET'])
def get_exercise():
    """
    Flalingo'dan transkript alıp analiz eder ve test oluşturur.
    """
    try:
        # API token ve report ID'yi al
        auth_token = request.args.get('auth_token')
        flai_report = request.args.get('flai_report')
        
        if not auth_token or not flai_report:
            return jsonify({
                'success': False,
                'error': 'auth_token ve flai_report parametreleri gerekli'
            }), 400
            
        # Flalingo'dan transkript al
        flalingo_service = FlalingoService()
        transcript_response = flalingo_service.get_transcript(auth_token, flai_report)
        
        if not transcript_response.get('success', False):
            return jsonify({
                'success': False,
                'error': transcript_response.get('error', 'Transkript alınamadı')
            }), 500
            
        # Transkript verisini işle
        transcript_data = transcript_response['data']
        processor = TranscriptProcessor(transcript_data)
        processed_data = processor.process_transcript()
        
        # AI analizi yap
        analyzer = AIAnalyzer()
        analysis_result = analyzer.analyze_zoom_transcript(processed_data)
        
        if not analysis_result.get('success', False):
            return jsonify({
                'success': False,
                'error': 'Transkript analizi başarısız'
            }), 500
            
        # Test oluştur
        tests_result = analyzer.generate_zoom_tests(analysis_result, processed_data)
        
        if not tests_result.get('success', False):
            return jsonify({
                'success': False,
                'error': 'Test oluşturma başarısız'
            }), 500
            
        # Test verilerini işle (JSON formatı için)
        test_generator = TestGenerator(tests_result.get('raw_tests', ''))
        test_generator.process_tests()
        processed_tests = test_generator.get_tests_as_json()  # Maksimum 10 soru
        
        return jsonify({
            'success': True,
            'data': {
                'analysis': analysis_result.get('raw_analysis', ''),
                'tests': processed_tests
            }
        })
        
    except Exception as e:
        logger.error(f"Exercise oluşturma sırasında hata: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'İşlem hatası: {str(e)}'
        }), 500

@app.route('/api/flai-exercise-completion', methods=['POST'])
def completion():
    """
    Egzersiz tamamlandığında kullanıcı cevaplarını değerlendirir.
    """
    try:
        data = request.get_json()
        auth_token = data.get('auth_token')
        flai_report = data.get('flai_report')
        exercise_response = data.get('exercise_response')
        
        if not all([auth_token, flai_report, exercise_response]):
            return jsonify({
                'success': False,
                'error': 'auth_token, flai_report ve exercise_response gerekli'
            }), 400
        
        # Cevapları kontrol et ve sonuçları hesapla
        correct = 0
        wrong = 0
        
        for answer in exercise_response:
            if answer.get('user_answer') == answer.get('correct_answer'):
                correct += 1
            else:
                wrong += 1
        
        # Özet oluştur
        summary = {
            'total_questions': len(exercise_response),
            'correct_answers': correct,
            'wrong_answers': wrong,
            'success_rate': (correct / len(exercise_response)) * 100 if exercise_response else 0
        }
        
        return jsonify({
            'success': True,
            'data': {
                'correct': correct,
                'wrong': wrong,
                'summary': summary
            }
        })
        
    except Exception as e:
        logger.error(f"Completion değerlendirme sırasında hata: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': str(error)
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error)
    }), 500 