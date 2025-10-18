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

@app.route('/health')
def health_check():
    """Cek status server"""
    return jsonify({
        'status': 'sehat',
        'timestamp': datetime.now().isoformat(),
        'model': 'whisper-base' if model else 'belum-dimuat',
        'bahasa': 'Indonesia',
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
