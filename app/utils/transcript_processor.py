import json
import re
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta

class TranscriptProcessor:
    """
    Transkript verilerini işleyen ve analiz eden sınıf.
    """
    
    def __init__(self, transcript_data: Dict[str, Any]):
        """
        TranscriptProcessor sınıfını başlatır.
        
        Args:
            transcript_data (Dict[str, Any]): Gladia'dan alınan transkript verisi
        """
        self.transcript_data = transcript_data
        self.processed_data = None
        
    def process_transcript(self) -> Dict[str, Any]:
        """
        Transkripti işler ve analiz için hazırlar.
        
        Returns:
            Dict[str, Any]: İşlenmiş transkript verileri.
        """
        if not self.transcript_data:
            print("Transkript verisi bulunamadı.")
            return {}
        
        # Gladia verisini işle
        gladia_data = self.transcript_data.get('gladia_response', [])
        
        # Konuşma istatistiklerini hesapla
        stats = self._calculate_statistics(gladia_data)
        
        # Kelime analizini yap
        vocabulary = self._analyze_vocabulary(gladia_data)
        
        # Sonuçları hazırla
        self.processed_data = {
            'gladia_response': gladia_data,
            'calculations': {
                'statistics': stats,
                'vocabulary': vocabulary
            }
        }
        
        return self.processed_data
    
    def _calculate_statistics(self, gladia_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Konuşma istatistiklerini hesaplar.
        
        Args:
            gladia_data: Gladia'dan gelen konuşma verileri
            
        Returns:
            Dict[str, Any]: Hesaplanan istatistikler
        """
        # Konuşmacıları gruplandır
        speakers = {}
        for entry in gladia_data:
            speaker = entry.get('speaker', 'Unknown')
            if speaker not in speakers:
                speakers[speaker] = []
            speakers[speaker].append(entry)
        
        # Her konuşmacı için istatistikler
        speaker_stats = {}
        for speaker, entries in speakers.items():
            total_words = sum(len(entry.get('text', '').split()) for entry in entries)
            total_time = sum(float(entry.get('duration', 0)) for entry in entries)
            
            speaker_stats[speaker] = {
                'total_utterances': len(entries),
                'total_words': total_words,
                'total_time': round(total_time, 2),
                'words_per_minute': round((total_words / total_time) * 60, 2) if total_time > 0 else 0
            }
        
        # Genel istatistikler
        total_time = sum(stats['total_time'] for stats in speaker_stats.values())
        total_words = sum(stats['total_words'] for stats in speaker_stats.values())
        
        return {
            'speaker_stats': speaker_stats,
            'total_time': round(total_time, 2),
            'total_words': total_words,
            'average_words_per_minute': round((total_words / total_time) * 60, 2) if total_time > 0 else 0
        }
    
    def _analyze_vocabulary(self, gladia_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Konuşmalardaki kelime kullanımını analiz eder.
        
        Args:
            gladia_data: Gladia'dan gelen konuşma verileri
            
        Returns:
            Dict[str, Any]: Kelime analizi sonuçları
        """
        # Tüm kelimeleri topla
        all_words = []
        for entry in gladia_data:
            text = entry.get('text', '').lower()
            # Noktalama işaretlerini kaldır
            text = re.sub(r'[^\w\s]', '', text)
            words = text.split()
            all_words.extend(words)
        
        # Kelime frekanslarını hesapla
        word_freq = {}
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # En sık kullanılan kelimeleri bul
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Kelime çeşitliliği
        vocabulary_size = len(set(all_words))
        total_words = len(all_words)
        
        return {
            'vocabulary_size': vocabulary_size,
            'total_words': total_words,
            'unique_words_ratio': round(vocabulary_size / total_words * 100, 2) if total_words > 0 else 0,
            'most_common_words': [{'word': word, 'count': count} for word, count in common_words],
            'word_frequency': word_freq
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """
        İşlenmiş verinin özetini oluşturur.
        
        Returns:
            Dict[str, Any]: Veri özeti
        """
        if not self.processed_data:
            print("Veri henüz işlenmemiş.")
            return {}
        
        stats = self.processed_data['calculations']['statistics']
        vocab = self.processed_data['calculations']['vocabulary']
        
        return {
            'duration': {
                'total_minutes': round(stats['total_time'] / 60, 2),
                'total_seconds': stats['total_time']
            },
            'speakers': {
                speaker: {
                    'talk_time_minutes': round(data['total_time'] / 60, 2),
                    'utterances': data['total_utterances'],
                    'words': data['total_words'],
                    'words_per_minute': data['words_per_minute']
                }
                for speaker, data in stats['speaker_stats'].items()
            },
            'vocabulary': {
                'unique_words': vocab['vocabulary_size'],
                'total_words': vocab['total_words'],
                'diversity_ratio': vocab['unique_words_ratio'],
                'top_words': vocab['most_common_words'][:10]  # İlk 10 kelime
            }
        } 