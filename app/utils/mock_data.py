"""
Frontend'den gelen istekler için mock veriler.
"""

# Frontend'den gelen ilk istek için mock data
MOCK_FRONTEND_REQUEST = {
    "api_token": "test_token_123",
    "flai_report": "report_123"
}

# Gladia'dan gelecek yanıt için mock data
MOCK_GLADIA_RESPONSE = {
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
        },
        {
            "speaker": "Teacher",
            "text": "That's wonderful! What was your favorite part about Paris?",
            "duration": 2.5,
            "confidence": 0.99
        },
        {
            "speaker": "Student",
            "text": "I loved the Eiffel Tower, especially at night when it was illuminated. The architecture was magnificent.",
            "duration": 5.1,
            "confidence": 0.96
        },
        {
            "speaker": "Teacher",
            "text": "Could you describe the food you tried there? Did you visit any traditional French restaurants?",
            "duration": 4.8,
            "confidence": 0.97
        },
        {
            "speaker": "Student",
            "text": "Yes, I tried escargot for the first time. It was interesting but different from what I expected. I also loved the croissants and baguettes.",
            "duration": 6.3,
            "confidence": 0.94
        }
    ]
}

MOCK_OPENAI_ANALYSIS = {
    "level": "B1",
    "strengths": [
        "Good vocabulary related to travel",
        "Able to express personal experiences",
        "Basic sentence construction"
    ],
    "areas_for_improvement": [
        "Advanced grammar structures",
        "More complex vocabulary usage",
        "Longer responses"
    ],
    "vocabulary": {
        "new_words": ["escargot", "illuminated", "magnificent", "architecture"],
        "expressions": ["for the first time", "different from what I expected"]
    },
    "topics": ["Travel", "Food", "Architecture"],
    "grammar": {
        "points_covered": ["Past tense", "Present tense"],
        "errors": ["Minor article usage"]
    },
    "pronunciation": {
        "strengths": ["Clear pronunciation of basic words"],
        "issues": ["Some difficulty with French words"]
    },
    "fluency": {
        "rating": "3/5",
        "comments": ["Generally good flow", "Some hesitation with complex topics"]
    }
}

MOCK_QUESTIONS = {
    "multiple_choice": [
        {
            "type": "multiple_choice",
            "question": "What city did the student visit?",
            "options": [
                {"id": "A", "text": "Paris"},
                {"id": "B", "text": "London"},
                {"id": "C", "text": "Rome"},
                {"id": "D", "text": "Madrid"}
            ],
            "correct_answer": "A",
            "explanation": "The student mentioned visiting Paris for the first time."
        },
        {
            "type": "multiple_choice",
            "question": "What French food did the student try?",
            "options": [
                {"id": "A", "text": "Croissants"},
                {"id": "B", "text": "Escargot"},
                {"id": "C", "text": "Baguettes"},
                {"id": "D", "text": "All of the above"}
            ],
            "correct_answer": "D",
            "explanation": "The student mentioned trying escargot, croissants, and baguettes."
        }
    ],
    "true_false": [
        {
            "type": "true_false",
            "question": "The student saw the Eiffel Tower at night.",
            "options": [
                {"id": "T", "text": "True"},
                {"id": "F", "text": "False"}
            ],
            "correct_answer": "T",
            "explanation": "The student mentioned seeing the Eiffel Tower illuminated at night."
        }
    ],
    "fill_in_blank": [
        {
            "type": "fill_in_blank",
            "question": "The student found the _____ of Paris to be magnificent.",
            "correct_answer": "architecture",
            "explanation": "The student specifically mentioned that the architecture was magnificent."
        }
    ]
}

# Frontend'den gelen cevaplar için mock data
MOCK_USER_ANSWERS = {
    "multiple_choice": [
        {"question_id": 0, "user_answer": "A"},
        {"question_id": 1, "user_answer": "D"}
    ],
    "true_false": [
        {"question_id": 0, "user_answer": "T"}
    ],
    "fill_in_blank": [
        {"question_id": 0, "user_answer": "architecture"}
    ]
}

MOCK_EVALUATION_RESULTS = {
    "summary": {
        "total_questions": 4,
        "correct_answers": 4,
        "wrong_answers": 0,
        "success_rate": 100.0
    },
    "by_question_type": {
        "multiple_choice": {
            "total": 2,
            "correct": 2,
            "wrong": 0,
            "success_rate": 100.0
        },
        "true_false": {
            "total": 1,
            "correct": 1,
            "wrong": 0,
            "success_rate": 100.0
        },
        "fill_in_blank": {
            "total": 1,
            "correct": 1,
            "wrong": 0,
            "success_rate": 100.0
        }
    }
} 