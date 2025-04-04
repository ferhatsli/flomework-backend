import pandas as pd
import re
import os
from typing import Dict, List, Any

class TranscriptProcessor:
    """
    Zoom ders transkriptlerini işleyen sınıf.
    """
    
    def __init__(self, file_path: str):
        """
        TranscriptProcessor sınıfını başlatır.
        
        Args:
            file_path (str): Transkript dosyasının yolu.
        """
        self.file_path = file_path
        self.transcript_data = None
        self.processed_data = None
        
    def load_transcript(self) -> bool:
        """
        Transkript dosyasını yükler.
        
        Returns:
            bool: Yükleme başarılı ise True, değilse False.
        """
        try:
            # Dosya uzantısına göre okuma yöntemi belirleme
            if self.file_path.endswith('.csv'):
                # CSV dosyasını okuma
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Konuşma verilerini ayıklama
                self.transcript_data = self._parse_transcript(content)
                return True
            elif self.file_path.endswith('.txt'):
                # TXT dosyasını okuma
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Konuşma verilerini ayıklama
                self.transcript_data = self._parse_txt_transcript(content)
                return True
            else:
                print(f"Desteklenmeyen dosya formatı: {self.file_path}")
                return False
        except Exception as e:
            print(f"Transkript yüklenirken hata oluştu: {str(e)}")
            return False
    
    def _parse_transcript(self, content: str) -> List[Dict[str, Any]]:
        """
        CSV transkript içeriğini ayrıştırır.
        
        Args:
            content (str): Transkript içeriği.
            
        Returns:
            List[Dict[str, Any]]: Ayrıştırılmış transkript verileri.
        """
        lines = content.split('\n')
        transcript_data = []
        
        i = 0
        while i < len(lines):
            # Zaman damgası ve konuşmacı bilgisini içeren satırları bul
            if '-->' in lines[i] and i > 0:
                # Önceki satır konuşma numarası
                index = lines[i-1].strip()
                
                # Zaman damgası
                time_line = lines[i].strip()
                time_match = re.search(r'(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)', time_line)
                
                if time_match and i+1 < len(lines):
                    start_time = time_match.group(1)
                    end_time = time_match.group(2)
                    
                    # Konuşmacı ve metin
                    speaker_text_line = lines[i+1].strip()
                    speaker_text_match = re.search(r'([^:]+): (.*)', speaker_text_line)
                    
                    if speaker_text_match:
                        speaker = speaker_text_match.group(1).strip()
                        text = speaker_text_match.group(2).strip()
                        
                        transcript_data.append({
                            'index': index,
                            'start_time': start_time,
                            'end_time': end_time,
                            'speaker': speaker,
                            'text': text
                        })
            i += 1
        
        return transcript_data
    
    def _parse_txt_transcript(self, content: str) -> List[Dict[str, Any]]:
        """
        Text formatındaki Zoom transkript içeriğini ayrıştırır.
        
        Args:
            content (str): Transkript içeriği.
            
        Returns:
            List[Dict[str, Any]]: Ayrıştırılmış transkript verileri.
        """
        lines = content.split('\n')
        transcript_data = []
        index = 1
        
        for line in lines:
            line = line.strip()
            if not line:  # Boş satırları atla
                continue
                
            # Konuşmacı ve metin formatını kontrol et: "Ad Soyad: Metin"
            speaker_text_match = re.search(r'^([^:]+):\s*(.*)', line)
            
            if speaker_text_match:
                speaker = speaker_text_match.group(1).strip()
                text = speaker_text_match.group(2).strip()
                
                # Zaman bilgisi olmadığı için indeks kullanılabilir
                transcript_data.append({
                    'index': str(index),
                    'start_time': '', # Text dosyasında zaman bilgisi olmayabilir
                    'end_time': '',
                    'speaker': speaker,
                    'text': text
                })
                index += 1
        
        return transcript_data
    
    def process_transcript(self) -> Dict[str, Any]:
        """
        Transkripti işler ve analiz için hazırlar.
        
        Returns:
            Dict[str, Any]: İşlenmiş transkript verileri.
        """
        if not self.transcript_data:
            print("Transkript verisi yüklenmemiş.")
            return {}
        
        # Konuşmacıları gruplandırma
        speakers = {}
        for entry in self.transcript_data:
            speaker = entry['speaker']
            if speaker not in speakers:
                speakers[speaker] = []
            speakers[speaker].append(entry['text'])
        
        # Her konuşmacının toplam konuşma sayısı
        speaker_counts = {speaker: len(texts) for speaker, texts in speakers.items()}
        
        # Tüm konuşma metinlerini birleştirme
        all_text = ' '.join([entry['text'] for entry in self.transcript_data])
        
        # Sonuçları hazırlama
        self.processed_data = {
            'speakers': speakers,
            'speaker_counts': speaker_counts,
            'all_text': all_text,
            'transcript_data': self.transcript_data
        }
        
        return self.processed_data
    
    def get_conversation_summary(self) -> str:
        """
        Konuşmanın özetini oluşturur.
        
        Returns:
            str: Konuşma özeti.
        """
        if not self.processed_data:
            print("Transkript işlenmemiş.")
            return ""
        
        # Konuşmacıları ve konuşma sayılarını içeren özet
        summary = "Konuşma Özeti:\n\n"
        
        # Konuşmacılar ve konuşma sayıları
        summary += "Konuşmacılar:\n"
        for speaker, count in self.processed_data['speaker_counts'].items():
            summary += f"- {speaker}: {count} konuşma\n"
        
        # Toplam konuşma sayısı
        total_entries = len(self.transcript_data)
        summary += f"\nToplam Konuşma Sayısı: {total_entries}\n"
        
        # Konuşma süresi (ilk ve son giriş arasındaki fark)
        if total_entries > 0:
            first_entry = self.transcript_data[0]
            last_entry = self.transcript_data[-1]
            if first_entry.get('start_time') and last_entry.get('end_time'):
                summary += f"İlk Konuşma Zamanı: {first_entry['start_time']}\n"
                summary += f"Son Konuşma Zamanı: {last_entry['end_time']}\n"
        
        return summary 