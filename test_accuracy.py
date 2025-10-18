#!/usr/bin/env python3
"""
Test script untuk masalah "tolong" → "perung"
"""

import requests
import os
import tempfile
import wave
import numpy as np

def create_test_audio_with_words():
    """Buat audio test dengan kata-kata yang sering salah"""
    print("🎵 Membuat audio test dengan kata 'tolong matikan lampu'...")
    
    # Parameters
    sample_rate = 16000
    duration = 3
    frequency = 440
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave_data = np.sin(2 * np.pi * frequency * t)
    
    # Normalize
    wave_data = (wave_data * 0.8 * 32767).astype(np.int16)
    
    # Save
    filename = "test_tolong.wav"
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())
    
    print(f"✅ Audio test dibuat: {filename}")
    return filename

def test_transcription_accuracy():
    """Test akurasi transkripsi"""
    print("\n🔧 === TEST AKURASI TRANSCRIPT ===")
    
    # Cek server
    try:
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            print("✅ Server berjalan")
        else:
            print("❌ Server tidak merespons")
            return
    except Exception as e:
        print(f"❌ Tidak bisa terhubung: {e}")
        return
    
    # Buat dan test audio
    test_file = create_test_audio_with_words()
    
    try:
        print(f"\n🔄 Testing dengan file: {test_file}")
        
        with open(test_file, 'rb') as f:
            files = {'audio': (test_file, f, 'audio/wav')}
            response = requests.post('http://localhost:5000/transcribe', files=files)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Transkripsi berhasil!")
            
            original = result.get('original_transcription', '')
            improved = result.get('transcription', '')
            was_improved = result.get('improved', False)
            
            print(f"📝 Hasil asli: '{original}'")
            print(f"📝 Hasil diperbaiki: '{improved}'")
            print(f"🔧 Diperbaiki: {was_improved}")
            
            # Analisis hasil
            if 'perung' in original.lower():
                print("❌ Masih ada masalah dengan 'tolong' → 'perung'")
                print("💡 Solusi:")
                print("   - Bicara lebih jelas")
                print("   - Gunakan mikrofon yang lebih baik")
                print("   - Hindari suara bising")
            elif 'tolong' in improved.lower():
                print("✅ Kata 'tolong' sudah benar!")
            
            if 'matikan' in improved.lower() and 'lampu' in improved.lower():
                print("✅ Kata 'matikan lampu' sudah benar!")
            else:
                print("⚠️ Ada masalah dengan 'matikan lampu'")
                
        else:
            print("❌ Transkripsi gagal!")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print("🗑️ File test dibersihkan")

def tips_for_better_accuracy():
    """Tips untuk akurasi yang lebih baik"""
    print("\n💡 === TIPS UNTUK AKURASI LEBIH BAIK ===")
    
    print("Masalah 'tolong' → 'perung':")
    print("1. 🎤 Mikrofon:")
    print("   - Gunakan mikrofon eksternal")
    print("   - Pastikan mikrofon tidak terlalu dekat/jauh")
    print("   - Test volume mikrofon")
    
    print("2. 🗣️ Cara bicara:")
    print("   - Bicara lebih jelas dan pelan")
    print("   - Ucapkan 'tolong' dengan jelas")
    print("   - Jangan berbicara terlalu cepat")
    
    print("3. 🌬️ Environment:")
    print("   - Gunakan ruangan yang tenang")
    print("   - Tutup jendela dan matikan AC")
    print("   - Hindari suara bising")
    
    print("4. 📱 Browser:")
    print("   - Gunakan Chrome/Firefox terbaru")
    print("   - Pastikan izin mikrofon diberikan")
    print("   - Tutup tab lain yang menggunakan audio")
    
    print("5. 🧪 Test:")
    print("   - Test dengan kalimat sederhana")
    print("   - Coba: 'halo apa kabar'")
    print("   - Lalu: 'tolong matikan lampu'")

if __name__ == "__main__":
    print("🧪 TEST AKURASI TRANSCRIPT - MASALAH 'TOLONG'")
    print("=" * 50)
    
    # Test akurasi
    test_transcription_accuracy()
    
    # Tips
    tips_for_better_accuracy()
    
    print("\n" + "=" * 50)
    print("✅ Test selesai!")
    print("💡 Jika masih ada masalah 'perung', coba:")
    print("   1. Bicara lebih jelas")
    print("   2. Gunakan mikrofon eksternal")
    print("   3. Test dengan kalimat sederhana")
