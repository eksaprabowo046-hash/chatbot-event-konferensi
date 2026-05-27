# 🎪 EventPro — Chatbot Manajemen Event & Konferensi

Chatbot berbasis **Finite State Automata (FSA)** untuk sistem registrasi event dan konferensi, dibangun menggunakan Python dan Streamlit.

## Fitur
- 🤖 Chatbot interaktif berbasis FSM (3 state: REGISTERING → CONFIRMING → COMPLETED)
- 🎪 6 paket event: Seminar, Workshop, Konferensi, Webinar, Gala Dinner, Bootcamp
- 🛒 Keranjang pendaftaran dinamis (tambah/hapus tiket)
- 💰 Kalkulasi total pembayaran otomatis
- 📋 Katalog event lengkap dengan info kapasitas & harga
- 🔄 NLP Engine dengan regex untuk deteksi intent dan parsing pesanan

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
