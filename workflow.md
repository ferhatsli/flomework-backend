# Flalingo API Akış Dokümantasyonu

## 1. Ders Bitişi ve İlk İstek
Frontend, ders bittikten sonra ilk isteği atar.

### Frontend → Backend İsteği:
```json
POST /api/flai-exercise
{
    "api_token": "gladia-api-token-123",
    "flai_report": "flai-report-id-123"
}
```

### Olası Hata Yanıtları:
```json
{
    "success": false,
    "error": {
        "code": "AUTH_ERROR",
        "message": "Invalid API token"
    }
}
```
veya
```json
{
    "success": false,
    "error": {
        "code": "REPORT_NOT_FOUND",
        "message": "Report ID not found"
    }
}
```

## 2. Transkript Alma
Backend, Gladia'dan tüm analiz verisini alır.

### Backend → Gladia İsteği:
```json
GET /api/transcript
{
    "api_token": "gladia-api-token-123",
    "flai_report": "flai-report-id-123"
}
```

### Gladia → Backend Yanıtı:
```json
{
    "openai": {
        "level": "B1",
        "strengths": [
            "Good vocabulary usage",
            "Clear pronunciation"
        ],
        "areas_for_improvement": [
            "Complex sentence structures",
            "Past tense usage"
        ],
        "vocabulary": {
            "new_words": ["magnificent", "illuminated"],
            "expressions": ["for the first time"]
        },
        "topics": ["Travel", "Food", "Architecture"],
        "grammar": {
            "points_covered": ["Past Simple", "Present Perfect"],
            "errors": []
        },
        "fluency": {
            "rating": "3/5",
            "comments": ["Good flow but could elaborate more"]
        }
    },
    "gladia_response": [
        {
            "speaker": "Teacher",
            "text": "Hello! How are you today? Let's talk about your recent travel experiences.",
            "duration": 4.2,
            "confidence": 0.98
        },
        {
            "speaker": "Student",
            "text": "Hi! I'm good, thank you. Last month, I visited Paris for the first time.",
            "duration": 3.8,
            "confidence": 0.95
        }
    ],
    "calculations": {
        "statistics": {
            "speaker_stats": {
                "Teacher": {
                    "total_utterances": 3,
                    "total_words": 36,
                    "total_time": 11.5,
                    "words_per_minute": 187.83
                },
                "Student": {
                    "total_utterances": 3,
                    "total_words": 54,
                    "total_time": 15.2,
                    "words_per_minute": 213.16
                }
            },
            "total_time": 26.7,
            "total_words": 90,
            "average_words_per_minute": 202.25
        },
        "vocabulary": {
            "vocabulary_size": 64,
            "total_words": 90,
            "unique_words_ratio": 71.11,
            "most_common_words": [
                {"word": "the", "count": 6},
                {"word": "you", "count": 5}
            ],
            "word_frequency": {
                "hello": 1,
                "how": 1
            }
        }
    }
}
```

## 3. Soru Üretimi ve Analiz
Backend, transkripti işler ve soruları üretir.

### Backend → Frontend Yanıtı:
```json
{
    "success": true,
    "data": {
        "analysis": {
            "level": "B1",
            "strengths": [
                "Good vocabulary usage",
                "Clear pronunciation"
            ],
            "areas_for_improvement": [
                "Complex sentence structures",
                "Past tense usage"
            ],
            "vocabulary": {
                "new_words": ["magnificent", "illuminated"],
                "expressions": ["for the first time"]
            },
            "topics": ["Travel", "Food", "Architecture"],
            "grammar": {
                "points_covered": ["Past Simple", "Present Perfect"],
                "errors": []
            },
            "fluency": {
                "rating": "3/5",
                "comments": ["Good flow but could elaborate more"]
            }
        },
        "statistics": {
            "speaker_stats": {
                "Teacher": {
                    "total_utterances": 3,
                    "total_words": 36,
                    "total_time": 11.5,
                    "words_per_minute": 187.83
                },
                "Student": {
                    "total_utterances": 3,
                    "total_words": 54,
                    "total_time": 15.2,
                    "words_per_minute": 213.16
                }
            },
            "total_time": 26.7,
            "total_words": 90,
            "average_words_per_minute": 202.25
        },
        "questions": {
            "multiple_choice": [
                {
                    "question_id": 1,
                    "type": "multiple_choice",
                    "question": "What did the speaker describe as magnificent?",
                    "options": [
                        {"id": "A", "text": "The architecture"},
                        {"id": "B", "text": "The food"},
                        {"id": "C", "text": "The weather"},
                        {"id": "D", "text": "The people"}
                    ]
                }
            ],
            "true_false": [
                {
                    "question_id": 1,
                    "type": "true_false",
                    "question": "The speaker visited Paris for the first time.",
                    "options": [
                        {"id": "T", "text": "True"},
                        {"id": "F", "text": "False"}
                    ]
                }
            ],
            "fill_in_blank": [
                {
                    "question_id": 1,
                    "type": "fill_in_blank",
                    "question": "The Eiffel Tower was _____ at night."
                }
            ]
        }
    }
}
```

## 4. Kullanıcı Cevapları
Frontend, kullanıcının cevaplarını gönderir.

### Frontend → Backend Cevap İsteği:
```json
POST /api/flai-exercise-completion
{
    "answers": {
        "multiple_choice": [
            {
                "question_id": 1,
                "user_answer": "A"
            }
        ],
        "true_false": [
            {
                "question_id": 1,
                "user_answer": "T"
            }
        ],
        "fill_in_blank": [
            {
                "question_id": 1,
                "user_answer": "illuminated"
            }
        ]
    }
}
```

## 5. Değerlendirme Sonuçları
Backend, cevapları değerlendirir ve sonuçları gönderir.

### Backend → Frontend Değerlendirme Yanıtı:
```json
{
    "success": true,
    "data": {
        "summary": {
            "total_questions": 20,
            "correct_answers": 15,
            "wrong_answers": 5,
            "success_rate": 75.0
        },
        "by_question_type": {
            "multiple_choice": {
                "total": 10,
                "correct": 8,
                "wrong": 2,
                "success_rate": 80.0
            },
            "true_false": {
                "total": 5,
                "correct": 4,
                "wrong": 1,
                "success_rate": 80.0
            },
            "fill_in_blank": {
                "total": 5,
                "correct": 3,
                "wrong": 2,
                "success_rate": 60.0
            }
        },
        "detailed_results": [
            {
                "question_id": 1,
                "question_type": "multiple_choice",
                "is_correct": true,
                "user_answer": "A",
                "correct_answer": "A",
                "explanation": "The architecture was indeed described as magnificent in the conversation."
            }
        ]
    }
}
```

## Genel Notlar

1. Tüm isteklerde header'da authentication token bulunmalıdır:
```
Authorization: Bearer <user-token>
Content-Type: application/json
```

2. Tüm yanıtlarda success/error durumu belirtilir:
```json
{
    "success": true/false,
    "data": {...}/null,
    "error": null/{"code": "...", "message": "..."}
}
```

3. HTTP Status Kodları:
- 200: Başarılı
- 400: Geçersiz istek
- 401: Yetkilendirme hatası
- 404: Kaynak bulunamadı
- 500: Sunucu hatası

4. Rate Limiting:
- Her IP için: 100 istek/dakika
- Her token için: 1000 istek/gün 