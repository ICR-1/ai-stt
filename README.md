# Voice Recorder dengan Whisper AI - Bahasa Indonesia

Sistem voice recording dan transkripsi dengan frontend web dan backend Python menggunakan OpenAI's Whisper AI, dioptimalkan untuk bahasa Indonesia.

## 🎯 Fitur Utama

- 🎤 **Voice Recording**: Rekam audio langsung di browser menggunakan mikrofon
- 📁 **File Upload**: Upload file audio yang sudah ada (WAV, MP3, M4A, OGG, FLAC, WEBM)
- 🤖 **AI Transcription**: Transkripsi otomatis speech-to-text menggunakan Whisper AI
- 🔊 **Text-to-Speech**: Konversi hasil transkripsi kembali ke audio dengan voice Indonesia yang natural
- 🇮🇩 **Bahasa Indonesia**: Dioptimalkan khusus untuk bahasa Indonesia
- ⚡ **Real-time Processing**: Transkripsi cepat dengan indikator progress
- 🎨 **Modern UI**: Interface yang indah dan responsif dengan desain glassmorphism

## 📦 File yang Tersedia

- `app_indonesia.py` - Server Flask backend utama
- `index.html` - Frontend web interface
- `requirements.txt` - Dependencies Python
- `README.md` - Dokumentasi ini

## 🚀 Cara Instalasi

1. **Install dependencies Python**:
```bash
pip install -r requirements.txt
```

2. **Jalankan server**:
```bash
   python app_indonesia.py
   ```

3. **Buka browser** dan kunjungi:
   ```
   http://localhost:5000
```

## 🎯 Cara Penggunaan

### Recording Audio
1. Klik tombol mikrofon untuk mulai merekam
2. Bicara ke mikrofon dengan jelas
3. Klik tombol stop ketika selesai
4. Klik "Proses dengan Whisper AI" untuk transkripsi

### Upload File
1. Klik "Pilih File Audio" untuk memilih file audio
2. Klik "Proses dengan Whisper AI" untuk transkripsi

### Melihat Hasil
- Hasil transkripsi akan muncul di area "Hasil Transkripsi"
- Anda bisa memutar ulang audio asli
- Waktu pemrosesan dan bahasa terdeteksi ditampilkan

### Text-to-Speech
- Setelah transkripsi selesai, klik tombol "Text-to-Speech"
- Sistem akan mengkonversi text ke audio dengan voice Indonesia yang natural
- Gunakan gTTS (Google) untuk voice yang lebih natural atau pyttsx3 (Local) untuk offline

## 🌐 API Endpoints

- `GET /` - Halaman utama
- `POST /transcribe` - Upload dan transkripsi audio
- `POST /tts` - Konversi text ke speech
- `GET /health` - Health check server
- `GET /debug/files` - Debug: lihat file yang tersimpan
- `GET /test-indonesia` - Test endpoint bahasa Indonesia
- `GET /audio/<filename>` - Serve file audio

## 📁 Format Audio yang Didukung

- WAV
- MP3
- M4A
- OGG
- FLAC
- WEBM

## 📊 Batasan File

- Maksimal ukuran file: 50MB

## 🇮🇩 Optimasi Bahasa Indonesia

Sistem ini dioptimalkan khusus untuk bahasa Indonesia dengan:

- **Language detection**: Otomatis mendeteksi bahasa Indonesia
- **Model configuration**: Pengaturan Whisper optimal untuk bahasa Indonesia
- **Error messages**: Pesan error dalam bahasa Indonesia
- **UI interface**: Interface dalam bahasa Indonesia

## 💡 Tips untuk Hasil Terbaik

1. **🎤 Mikrofon**: Gunakan mikrofon berkualitas baik
2. **🗣️ Cara bicara**: Bicara dengan jelas dan tidak terlalu cepat
3. **🌬️ Environment**: Gunakan ruangan yang tenang, hindari suara bising
4. **📱 Browser**: Gunakan Chrome/Firefox terbaru
5. **⏱️ Durasi**: Rekam minimal 2-3 detik untuk hasil optimal

## 🔧 Troubleshooting

### Mikrofon Tidak Berfungsi
- Pastikan browser memiliki izin akses mikrofon
- Cek pengaturan mikrofon di sistem
- Coba refresh halaman

### Hasil Transkripsi Buruk
- Pastikan bicara dengan jelas
- Hindari suara bising di background
- Test dengan kalimat sederhana: "halo apa kabar"
- Gunakan mikrofon eksternal jika memungkinkan

### Server Tidak Berjalan
- Pastikan port 5000 tidak digunakan aplikasi lain
- Cek bahwa semua dependencies terinstall
- Pastikan Python versi 3.7+ terinstall

### File Upload Gagal
- Pastikan file dalam format yang didukung
- Cek ukuran file (maksimal 50MB)
- Pastikan file tidak korup

### TTS Voice Tidak Natural
- Sistem menggunakan gTTS (Google) sebagai default untuk voice Indonesia yang lebih natural
- Jika ingin offline, gunakan pyttsx3 (Local) tapi mungkin aksen Inggris
- Untuk voice Indonesia yang lebih baik, install Indonesian language pack di Windows

## 📝 Model Whisper

Sistem menggunakan model "base" yang memberikan keseimbangan optimal antara:
- **Kecepatan**: Cukup cepat untuk penggunaan real-time
- **Akurasi**: Akurat untuk bahasa Indonesia
- **Ukuran**: Tidak terlalu besar (74 MB)

## 🛠️ Development

Untuk development atau modifikasi:

1. Edit `app_indonesia.py` untuk backend
2. Edit `index.html` untuk frontend
3. Restart server untuk melihat perubahan

## 📄 License

Project ini open source dan tersedia di bawah MIT License.

---

**Selamat menggunakan Voice Recorder dengan Whisper AI! 🎉**