# 🎪 EventPro Concierge — Premium Event Management System

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B.svg)
![Status](https://img.shields.io/badge/Status-Premium_Version-gold.svg)

Sistem Manajemen Event cerdas dengan antarmuka **Conversational UI** berbasis **Finite State Automata (FSA)**. Proyek ini menggabungkan NLP Engine kustom untuk memproses pendaftaran event, seminar, dan konferensi secara natural.

## Fitur
- 🤖 **Hybrid Conversational UI**: Seluruh alur pendaftaran, pemilihan paket, hingga pengisian form dilakukan di dalam satu jendela chat yang elegan.
- ⚙️ **FSM Architecture**: Logika state machine yang solid (REGISTERING, CONFIRMING, COMPLETED) untuk memastikan alur data yang akurat.
- 📊 **In-Chat Dashboard**: Visualisasi statistik pendaftaran dan status sistem yang muncul secara dinamis lewat perintah chat.
- 🛒 **Dynamic Smart Cart**: Mendukung pemrosesan bahasa alami untuk menambah atau mengurangi tiket (contoh: *"tambah 2 workshop dan batalkan seminar"*).
- 📝 **Embedded Smart Form**: Integrasi form identitas yang muncul secara otomatis setelah konfirmasi reservasi.

## Cara Menjalankan
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Struktur Proyek

```
Chatbot_Event_Konferensi/
├── app.py          # Frontend Streamlit
├── event_fsm.py    # Finite State Machine (FSM)
├── engine.py       # NLP Engine (parsing & intent detection)
├── requirements.txt
└── README.md
```

## Contoh Perintah Chat
- `paket` — lihat daftar event
- `daftar 1 konferensi` — daftar 1 tiket konferensi
- `daftar 2 webinar dan 1 workshop` — daftar beberapa event sekaligus
- `batalkan 1 webinar` — hapus tiket dari keranjang
- `checkout` / `bayar` — konfirmasi pendaftaran
- `reset` — mulai ulang dari awal

## Teknologi
- Python 3.x
- Streamlit
- Regex (re module)
- Enum (FSM states)
