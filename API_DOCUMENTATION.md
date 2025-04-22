# Flalingo Exercise API Documentation

## Base URL
```
https://exercise.flalingo.com
```

## Transcript Format
Flalingo API'den gelen transkript verisi aşağıdaki formatta olmalıdır:

```json
{
    "success": true,
    "data": {
        "transcript": {
            "speakers": {
                "Speaker 1": [
                    "Hello, how are you today?",
                    "Let's start our lesson."
                ],
                "Speaker 2": [
                    "I'm fine, thank you.",
                    "Yes, I'm ready to begin."
                ]
            },
            "speaker_counts": {
                "Speaker 1": 10,
                "Speaker 2": 8
            },
            "all_text": "Complete conversation text here...",
            "metadata": {
                "duration": "30:00",
                "date": "2024-03-20",
                "lesson_topic": "Business English"
            }
        }
    }
}
```

### Transcript Fields
- **speakers**: Her konuşmacının konuşma metinlerini içeren obje
  - Key: Konuşmacı adı
  - Value: Konuşmacının sıralı konuşma metinleri (array)
- **speaker_counts**: Her konuşmacının toplam konuşma sayısı
- **all_text**: Tüm konuşmanın birleştirilmiş hali
- **metadata**: Ders ile ilgili ek bilgiler
  - duration: Dersin süresi
  - date: Dersin tarihi
  - lesson_topic: Dersin konusu

### Önemli Notlar
1. Konuşmacı isimleri tutarlı olmalıdır
2. Konuşma metinleri kronolojik sırada olmalıdır
3. Her konuşma metni tam ve anlamlı cümleler içermelidir
4. Metadata alanındaki bilgiler opsiyoneldir

## Endpoints

### 1. Custom Exercise Redirect
Kullanıcıyı egzersiz sayfasına yönlendirir.

**Endpoint:** `GET /your-custom-exercise`

**Parameters:**
```
auth_token: string (required)
flai_report: string (required)
```

**Example Request:**
```
GET /your-custom-exercise?auth_token=xyz789&flai_report=abc123
```

**Success Response:**
```
Redirects to: /api/flai-exercise?auth_token=xyz789&flai_report=abc123
```

**Error Response:**
```json
{
    "success": false,
    "error": "auth_token ve flai_report parametreleri gerekli"
}
```

### 2. Get Exercise
Transkript verisi alır, analiz eder ve test soruları oluşturur.

**Endpoint:** `GET /api/flai-exercise`

**Parameters:**
```
auth_token: string (required)
flai_report: string (required)
```

**Example Request:**
```
GET /api/flai-exercise?auth_token=xyz789&flai_report=abc123
```

**Success Response:**
```json
{
    "success": true,
    "data": {
        "analysis": {
            "student_level": "B2",
            "strengths": ["vocabulary", "fluency"],
            "areas_to_improve": ["grammar", "pronunciation"],
            "learned_words": ["collaborate", "implement"],
            "main_topics": ["business communication"]
        },
        "tests": [
            {
                "question": "What is the main purpose of...",
                "options": [
                    {"letter": "A", "text": "To improve communication"},
                    {"letter": "B", "text": "To increase sales"},
                    {"letter": "C", "text": "To reduce costs"},
                    {"letter": "D", "text": "To expand market"}
                ],
                "correct_answer": "A",
                "explanation": "The context clearly indicates..."
            }
            // ... toplam 10 soru
        ]
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "Transkript alınamadı"
}
```

### 3. Exercise Completion
Kullanıcının test cevaplarını alır ve sonuçları değerlendirir.

**Endpoint:** `POST /api/flai-exercise-completion`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {auth_token}
```

**Request Body:**
```json
{
    "auth_token": "xyz789",
    "flai_report": "abc123",
    "exercise_response": [
        {
            "question_id": 1,
            "user_answer": "A",
            "correct_answer": "A"
        },
        {
            "question_id": 2,
            "user_answer": "B",
            "correct_answer": "C"
        }
        // ... diğer cevaplar
    ]
}
```

**Success Response:**
```json
{
    "success": true,
    "data": {
        "correct": 7,
        "wrong": 3,
        "summary": {
            "total_questions": 10,
            "correct_answers": 7,
            "wrong_answers": 3,
            "success_rate": 70.0
        }
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "auth_token, flai_report ve exercise_response gerekli"
}
```

## Error Codes

### HTTP Status Codes
- **200:** Başarılı
- **400:** Geçersiz istek (eksik veya hatalı parametreler)
- **404:** Endpoint bulunamadı
- **500:** Sunucu hatası

### Common Error Responses
```json
{
    "success": false,
    "error": "Error message",
    "message": "Detailed error description"
}
```

## Notes
1. Tüm istekler `exercise.flalingo.com` domain'i üzerinden yapılmalıdır
2. `auth_token` her istekte gereklidir
3. Test soruları her zaman maksimum 10 adet olacaktır
4. Frontend, soruları gösterirken 30 saniye boyunca statik tips göstermelidir 