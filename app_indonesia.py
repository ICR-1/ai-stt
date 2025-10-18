#!/usr/bin/env python3
"""
Flask Server untuk Whisper AI - Optimized untuk Bahasa Indonesia
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import whisper
import os
import uuid
import time
from datetime import datetime
import warnings
import pyttsx3
from gtts import gTTS
import threading

# Suppress warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("🔄 Memuat model Whisper...")
try:
    # Load model dengan konfigurasi untuk CPU
    model = whisper.load_model("base")
    print("✅ Model Whisper berhasil dimuat!")
except Exception as e:
    print(f"❌ Gagal memuat model: {e}")
    model = None

def improve_transcription(text):
    """Perbaiki hasil transkripsi dengan koreksi kata umum"""
    if not text:
        return text
    
    # Koreksi kata-kata yang sering salah dalam bahasa Indonesia
    corrections = {
        'perung': 'tolong',
        'perong': 'tolong', 
        'perong': 'tolong',
        'tolong': 'tolong',
        'matikan': 'matikan',
        'lampu': 'lampu',
        'nyalakan': 'nyalakan',
        'buka': 'buka',
        'tutup': 'tutup',
        'halo': 'halo',
        'apa': 'apa',
        'kabar': 'kabar',
        'baik': 'baik',
        'saja': 'saja',
        'terima': 'terima',
        'kasih': 'kasih',
        'sama': 'sama',
        'sama-sama': 'sama-sama'
    }
    
    # Split text dan perbaiki setiap kata
    words = text.lower().split()
    corrected_words = []
    
    for word in words:
        # Hapus tanda baca untuk matching
        clean_word = word.strip('.,!?')
        if clean_word in corrections:
            corrected_words.append(corrections[clean_word])
        else:
            corrected_words.append(word)
    
    return ' '.join(corrected_words)

def text_to_speech(text, filename):
    """Konversi text ke speech menggunakan pyttsx3 dengan optimasi bahasa Indonesia"""
    try:
        print(f"🔊 Mengkonversi text ke speech: '{text[:50]}...'")
        
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Dapatkan semua voice yang tersedia
        voices = engine.getProperty('voices')
        print(f"📢 Total voices tersedia: {len(voices)}")
        
        # Cari voice Indonesia atau yang paling cocok
        best_voice = None
        indonesian_voice = None
        
        for i, voice in enumerate(voices):
            voice_name = voice.name.lower()
            voice_id = voice.id.lower()
            
            print(f"Voice {i}: {voice.name} ({voice.id})")
            
            # Prioritas 1: Voice Indonesia eksplisit
            if any(keyword in voice_name for keyword in ['indonesia', 'indonesian', 'bahasa indonesia']):
                indonesian_voice = voice
                print(f"✅ Found Indonesian voice: {voice.name}")
                break
            
            # Prioritas 2: Voice Asia Tenggara
            elif any(keyword in voice_name for keyword in ['malay', 'malaysia', 'singapore', 'asian']):
                if not best_voice:
                    best_voice = voice
                    print(f"🔄 Found Asian voice: {voice.name}")
            
            # Prioritas 3: Voice dengan bahasa yang lebih netral
            elif any(keyword in voice_name for keyword in ['neutral', 'universal', 'multilingual']):
                if not best_voice:
                    best_voice = voice
                    print(f"🔄 Found neutral voice: {voice.name}")
        
        # Pilih voice terbaik
        selected_voice = indonesian_voice or best_voice
        
        if selected_voice:
            engine.setProperty('voice', selected_voice.id)
            print(f"🎤 Menggunakan voice: {selected_voice.name}")
        else:
            print("⚠️ Menggunakan voice default")
        
        # Konfigurasi optimal untuk bahasa Indonesia
        engine.setProperty('rate', 140)    # Sedikit lebih lambat untuk kejelasan
        engine.setProperty('volume', 0.9)  # Volume tinggi
        
        # Simpan ke file dengan format yang lebih baik
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Gunakan format WAV untuk kualitas terbaik
        engine.save_to_file(text, filepath)
        engine.runAndWait()
        
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✅ TTS file tersimpan: {filepath} ({file_size:,} bytes)")
            return filepath
        else:
            print("❌ Gagal menyimpan file TTS")
            return None
            
    except Exception as e:
        print(f"❌ Error TTS: {e}")
        return None

def text_to_speech_gtts(text, filename):
    """Konversi text ke speech menggunakan gTTS (Google Text-to-Speech) - Voice Indonesia yang lebih baik"""
    try:
        print(f"🔊 Mengkonversi text ke speech dengan gTTS: '{text[:50]}...'")
        
        # Buat TTS dengan bahasa Indonesia
        tts = gTTS(text=text, lang='id', slow=False)
        
        # Simpan ke file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        tts.save(filepath)
        
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✅ TTS gTTS file tersimpan: {filepath} ({file_size:,} bytes)")
            return filepath
        else:
            print("❌ Gagal menyimpan file TTS gTTS")
            return None
            
    except Exception as e:
        print(f"❌ Error TTS gTTS: {e}")
        return None

@app.route('/')
def index():
    """Halaman utama"""
    return send_file('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Endpoint untuk transkripsi audio"""
    try:
        print(f"\n🎤 === PERMINTAAN TRANSCRIPT BARU ===")
        print(f"⏰ Waktu: {datetime.now().strftime('%H:%M:%S')}")
        
        # Cek apakah ada file audio
        if 'audio' not in request.files:
            print("❌ Tidak ada file audio dalam request")
            return jsonify({
                'success': False, 
                'error': 'Tidak ada file audio yang dikirim'
            }), 400
        
        file = request.files['audio']
        if not file.filename:
            print("❌ Tidak ada nama file")
            return jsonify({
                'success': False, 
                'error': 'Tidak ada file yang dipilih'
            }), 400
        
        print(f"📁 File: {file.filename}")
        print(f"📁 Tipe konten: {file.content_type}")
        
        # Simpan file
        filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            file.save(filepath)
            file_size = os.path.getsize(filepath)
            print(f"✅ File tersimpan: {filepath}")
            print(f"📊 Ukuran file: {file_size:,} bytes")
            
            if file_size == 0:
                raise ValueError("File kosong")
                
        except Exception as e:
            print(f"❌ Gagal menyimpan file: {e}")
            return jsonify({
                'success': False, 
                'error': f'Gagal menyimpan file: {str(e)}'
            }), 400
        
        try:
            # Transkripsi dengan Whisper
            print("🔄 Memulai transkripsi...")
            
            if model is None:
                raise Exception("Model Whisper belum dimuat")
            
            # Konfigurasi optimal untuk bahasa Indonesia
            transcribe_options = {
                "language": "id",  # Bahasa Indonesia
                "fp16": False,    # Gunakan FP32 untuk CPU
                "verbose": False,
                "temperature": 0.0,  # Lebih deterministik
                "best_of": 3,        # Coba 3 kali, ambil yang terbaik
                "beam_size": 5,      # Beam search untuk akurasi lebih baik
                "patience": 1.0,     # Lebih sabar dalam decoding
                "length_penalty": 1.0,  # Penalty untuk panjang
                "suppress_tokens": [-1],  # Suppress empty tokens
                "initial_prompt": "Ini adalah transkripsi dalam bahasa Indonesia. Tolong matikan lampu."  # Prompt untuk konteks
            }
            
            start_time = time.time()
            result = model.transcribe(filepath, **transcribe_options)
            processing_time = time.time() - start_time
            
            transcription_text = result['text'].strip()
            detected_language = result.get('language', 'id')
            
            # Perbaiki hasil transkripsi
            original_text = transcription_text
            transcription_text = improve_transcription(transcription_text)
            
            print(f"✅ Transkripsi selesai dalam {processing_time:.2f} detik")
            print(f"📝 Hasil asli: '{original_text}'")
            print(f"📝 Hasil diperbaiki: '{transcription_text}'")
            print(f"🌍 Bahasa terdeteksi: {detected_language}")
            
            # Response
            response_data = {
                'success': True,
                'transcription': transcription_text,
                'original_transcription': original_text,
                'language': detected_language,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat(),
                'message': 'Transkripsi berhasil!',
                'improved': original_text != transcription_text
            }
            
            # Tambahkan URL audio jika ada hasil
            if transcription_text:
                response_data['audio_url'] = f"/audio/{filename}"
            
            return jsonify(response_data)
            
        except Exception as e:
            print(f"❌ Error transkripsi: {e}")
            return jsonify({
                'success': False, 
                'error': f'Gagal transkripsi: {str(e)}'
            }), 500
            
        finally:
            # Bersihkan file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    print(f"🗑️ File dibersihkan: {filepath}")
                except Exception as e:
                    print(f"⚠️ Tidak bisa menghapus file: {e}")
    
    except Exception as e:
        print(f"❌ Error endpoint transcribe: {e}")
        return jsonify({
            'success': False, 
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve file audio"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath)
        else:
            return jsonify({'error': 'File audio tidak ditemukan'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tts', methods=['POST'])
def text_to_speech_endpoint():
    """Endpoint untuk Text-to-Speech"""
    try:
        print(f"\n🔊 === PERMINTAAN TTS BARU ===")
        print(f"⏰ Waktu: {datetime.now().strftime('%H:%M:%S')}")
        
        # Get text from request
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Tidak ada text yang dikirim'
            }), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text kosong'
            }), 400
        
        use_gtts = data.get('use_gtts', True)  # Default menggunakan gTTS
        print(f"📝 Text untuk TTS: '{text}' (gTTS: {use_gtts})")
        
        # Generate filename berdasarkan method
        if use_gtts:
            tts_filename = f"tts_{uuid.uuid4()}.mp3"
            tts_filepath = text_to_speech_gtts(text, tts_filename)
            tts_method = "gTTS (Google)"
        else:
            tts_filename = f"tts_{uuid.uuid4()}.wav"
            tts_filepath = text_to_speech(text, tts_filename)
            tts_method = "pyttsx3 (Local)"
        
        if tts_filepath:
            return jsonify({
                'success': True,
                'text': text,
                'audio_url': f"/audio/{tts_filename}",
                'filename': tts_filename,
                'timestamp': datetime.now().isoformat(),
                'message': f'TTS berhasil dibuat dengan {tts_method}',
                'method': tts_method
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Gagal membuat TTS'
            }), 500
            
    except Exception as e:
        print(f"❌ Error TTS endpoint: {e}")
        return jsonify({
            'success': False,
            'error': f'TTS error: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """Cek status server"""
    return jsonify({
        'status': 'sehat',
        'timestamp': datetime.now().isoformat(),
        'model': 'whisper-base' if model else 'belum-dimuat',
        'bahasa': 'Indonesia',
        'tts': 'gTTS (Google) + pyttsx3 (Local)',
        'pesan': 'Server berjalan dengan baik'
    })

@app.route('/debug/files')
def debug_files():
    """Debug: lihat file yang tersimpan"""
    try:
        files_info = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    files_info.append({
                        'filename': filename,
                        'size': os.path.getsize(filepath),
                        'path': filepath,
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    })
        
        return jsonify({
            'upload_folder': UPLOAD_FOLDER,
            'folder_exists': os.path.exists(UPLOAD_FOLDER),
            'files': files_info,
            'total_files': len(files_info),
            'message': 'Daftar file berhasil diambil'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-indonesia')
def test_indonesia():
    """Test endpoint untuk bahasa Indonesia"""
    return jsonify({
        'message': 'Halo! Server Whisper AI berjalan dengan baik.',
        'bahasa': 'Indonesia',
        'status': 'OK',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/tts-voices')
def list_tts_voices():
    """List semua voice TTS yang tersedia"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        voice_list = []
        for i, voice in enumerate(voices):
            voice_info = {
                'index': i,
                'name': voice.name,
                'id': voice.id,
                'is_indonesian': any(keyword in voice.name.lower() for keyword in ['indonesia', 'indonesian', 'bahasa indonesia']),
                'is_asian': any(keyword in voice.name.lower() for keyword in ['malay', 'malaysia', 'singapore', 'asian']),
                'is_neutral': any(keyword in voice.name.lower() for keyword in ['neutral', 'universal', 'multilingual'])
            }
            voice_list.append(voice_info)
        
        return jsonify({
            'total_voices': len(voices),
            'voices': voice_list,
            'message': 'Daftar voice TTS tersedia'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Gagal mendapatkan daftar voice'
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎤 SERVER WHISPER AI - BAHASA INDONESIA")
    print("="*60)
    print("🌐 Server: http://localhost:5000")
    print("🔍 Health: http://localhost:5000/health")
    print("📁 Debug: http://localhost:5000/debug/files")
    print("🇮🇩 Test ID: http://localhost:5000/test-indonesia")
    print("="*60)
    print("💡 Tips:")
    print("   - Bicara dengan jelas dalam bahasa Indonesia")
    print("   - Hindari suara bising di background")
    print("   - Rekam minimal 2-3 detik")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
