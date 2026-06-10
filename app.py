import streamlit as st
import re

# 1. INITIAL SETTING DASHBOARD WIDE
st.set_page_config(
    page_title="EventPro Executive Dashboard", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# KUSTOMISASI CSS SPESIFIK: Mengubah warna container luar input chat menjadi Hijau Muda/Sage Soft
st.markdown("""
    <style>
    /* Latar Belakang Utama */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0f172a !important;
        color: #f1f5f9 !important;
    }
    
    /* FORCE WARNA TEKS CHAT BOX: Memastikan teks putih bersih */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] span, 
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] div {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* FIX BLOK PUTIH MARKDOWN: Menghilangkan background putih kaku pada inline code */
    [data-testid="stChatMessage"] code {
        background-color: transparent !important;
        color: #f59e0b !important;
        font-size: 14px !important;
        font-weight: bold !important;
        padding: 0px 4px !important;
        border: none !important;
    }
    
    /* Menghilangkan avatar bawaan Streamlit */
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    
    /* Desain Container Bubble Chat */
    [data-testid="stChatMessage"] {
        background-color: #1e293b !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        padding: 14px 18px !important;
        border: 1px solid #334155 !important;
    }
    
    /* ============================================================== */
    /* FIX TOTAL INPUT CHATBOX (MENGHILANGKAN BLOK PUTIH & HITAM)     */
    /* ============================================================== */
    
    /* 1. Container Paling Luar (Yang tadinya putih lebar) */
    [data-testid="stChatInput"] {
        background-color: #0369a1 !important; /* Biru muda profesional */
        border: 2px solid #38bdf8 !important;  /* Border biru senada */
        border-radius: 12px !important;
        padding: 6px !important;
    }
    
    /* 2. Form pembungkus internal */
    [data-testid="stChatInput"] div {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* 3. Area teks tempat mengetik (Menghilangkan blok hitam tengah) */
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;             /* Teks ketikan putih bersih */
        background-color: transparent !important; /* Mengikuti warna dasar hijau container */
        border: none !important;
        box-shadow: none !important;
    }
    
    /* 4. Warna placeholder petunjuk teks */
    [data-testid="stChatInput"] textarea::placeholder {
        color: #bae6fd !important;             /* Teks hint biru muda pudar */
    }
    
    /* 5. Tombol panah kirim (Kanan) */
    [data-testid="stChatInput"] button {
        background-color: #38bdf8 !important;
        color: #ffffff !important;
        border-radius: 50% !important;
    }
    /* ============================================================== */
    
    /* Tombol Utama Pro */
    div.stButton > button {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 6px !important;
        font-weight: bold !important;
    }
    
    /* Tombol Filter "Lihat Semua Event" */
    div.stButton > button[key="btn_semua"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        height: 45px !important;
    }
    
    /* Tombol Filter "Event Gratis" */
    div.stButton > button[key="btn_gratis"] {
        background-color: #059669 !important;
        color: #ffffff !important;
        border: 2px solid #34d399 !important;
        height: 45px !important;
    }
    
    .left-scroll-box {
        max-height: 520px;
        overflow-y: auto;
        padding-right: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MASTER DATA ACARA - 10 EVENT LENGKAP
if 'db_events' not in st.session_state:
    st.session_state.db_events = [
        {"id": 1, "judul": "Seminar Nasional AI & Masa Depan Kerja", "category": "Seminar", "harga_int": 25000, "harga": "Rp 25.000", "status_label": "🔴 BERBAYAR", "tanggal": "25 Okt 2026", "pembicara": "Dr. Eksa Prabowo", "deskripsi": "Membahas implementasi kecerdasan buatan dalam dunia kerja modern."},
        {"id": 2, "judul": "Workshop Koding: Svelte & Go Webview", "category": "Workshop", "harga_int": 50000, "harga": "Rp 50.000", "status_label": "🔴 BERBAYAR", "tanggal": "10 Nov 2026", "pembicara": "Heksa Federica", "deskripsi": "Praktik langsung membuat aplikasi desktop/mobile webview handal."},
        {"id": 3, "judul": "National Hackathon 2026: IoT Pertanian", "category": "Lomba", "harga_int": 75000, "harga": "Rp 75.000", "status_label": "🔴 BERBAYAR", "tanggal": "15 Des 2026", "pembicara": "Juri Profesional", "deskripsi": "Kompetisi koding intensif menciptakan inovasi perangkat pintar IoT."},
        {"id": 4, "judul": "UI/UX Deep Dive Challenge: Figma App", "category": "Lomba", "harga_int": 20000, "harga": "Rp 20.000", "status_label": "🔴 BERBAYAR", "tanggal": "20 Agu 2026", "pembicara": "Zaka (PT DSI)", "deskripsi": "Tantangan merancang ulang sistem desain antarmuka skala industri."},
        {"id": 5, "judul": "Webinar Coding Basic untuk Pemula", "category": "Seminar", "harga_int": 0, "harga": "GRATIS", "status_label": "🟢 GRATIS", "tanggal": "01 Sep 2026", "pembicara": "Dev Team IT", "deskripsi": "Pengenalan dasar pemrograman web menggunakan HTML, CSS, dan JS."},
        {"id": 6, "judul": "Workshop IoT Keamanan Rumah Pintar", "category": "Workshop", "harga_int": 0, "harga": "GRATIS", "status_label": "🟢 GRATIS", "tanggal": "12 Nov 2026", "pembicara": "Riset Team", "deskripsi": "Membangun sistem keamanan rumah terintegrasi notifikasi bahaya."},
        {"id": 7, "judul": "Seminar Technopreneurship & Startup Digital", "category": "Seminar", "harga_int": 0, "harga": "GRATIS", "status_label": "🟢 GRATIS", "tanggal": "05 Okt 2026", "pembicara": "CEO Muda Indonesia", "deskripsi": "Tips dan trik membangun bisnis rintisan teknologi digital."},
        {"id": 8, "judul": "Mastering Flutter State Management", "category": "Workshop", "harga_int": 90000, "harga": "Rp 90.000", "status_label": "🔴 BERBAYAR", "tanggal": "18 Nov 2026", "pembicara": "Senior Mobile Dev", "deskripsi": "Pendalaman arsitektur manajemen state Flutter menggunakan Bloc."},
        {"id": 9, "judul": "Webinar Cyber Security: Ethical Hacking", "category": "Seminar", "harga_int": 35000, "harga": "Rp 35.000", "status_label": "🔴 BERBAYAR", "tanggal": "28 Des 2026", "pembicara": "Security Analyst", "deskripsi": "Eksplorasi teknik penetration testing dasar dan penutupan celah."},
        {"id": 10, "judul": "Lomba Desain Landing Page Nasional", "category": "Lomba", "harga_int": 0, "harga": "GRATIS", "status_label": "🟢 GRATIS", "tanggal": "14 Jan 2027", "pembicara": "Expert UI Designer", "deskripsi": "Kompetisi adu kreativitas menyusun layout landing page konversif."},
    ]

# Inisialisasi State Manajemen Transaksi
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "🤖 **Sistem:** Halo! Silakan ketik langsung **Nomor Kode Event** yang ingin kamu daftarkan di bawah (Contoh: `1` atau `1, 2`). Sistem otomatis memproses kalkulasi tagihan Anda."}]
if 'reg_status' not in st.session_state:
    st.session_state.reg_status = "idle"
if 'selected_event_id' not in st.session_state:
    st.session_state.selected_event_id = 1
if 'cart_event_ids' not in st.session_state:
    st.session_state.cart_event_ids = []
if 'reg_data' not in st.session_state:
    st.session_state.reg_data = {}
if 'filter_harga' not in st.session_state:
    st.session_state.filter_harga = "Semua"
if 'pembayaran_sukses_data' not in st.session_state:
    st.session_state.pembayaran_sukses_data = None

# ==================== BANNER UTAMA DASHBOARD ====================
st.title("🏛️ EventPro Executive Dashboard")
st.caption("Sistem Otomasi Pendaftaran Event Berbasis Input Nomor Kode Cepat & Integrasi Struk Panel Detail")
st.write("---")

# ==================== STRUKTUR LAYOUT UTAMA ====================
kolom_kiri, kolom_kanan = st.columns([1.2, 1.2])

# -------------------- KOLOM KIRI: DAFTAR KONTEN EVENT --------------------
with kolom_kiri:
    st.subheader("✨ Pilihan Pendaftaran Event")
    
    cf1, cf2 = st.columns([1, 1])
    with cf1:
        if st.button("📋 Lihat Semua Event", key="btn_semua", use_container_width=True):
            st.session_state.filter_harga = "Semua"
    with cf2:
        if st.button("🎁 Event Gratis", key="btn_gratis", use_container_width=True):
            st.session_state.filter_harga = "Gratis"
            
    st.write(f"Kategori Filter Terpilih: **{st.session_state.filter_harga}**")
    
    if st.session_state.filter_harga == "Gratis":
        filtered_events = [x for x in st.session_state.db_events if x['harga_int'] == 0]
    else:
        filtered_events = st.session_state.db_events

    st.markdown('<div class="left-scroll-box">', unsafe_allow_html=True)
    for item in filtered_events:
        badge_color = "#10b981" if item['harga_int'] == 0 else "#ef4444"
        
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 14px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid {badge_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #38bdf8; font-weight: bold; font-size: 13px;">👉 KODE NOMOR: {item['id']} ({item['category']})</span>
                    <span style="background-color: {badge_color}; color: white; font-size: 10px; padding: 3px 6px; border-radius: 4px; font-weight: bold;">{item['status_label']}</span>
                </div>
                <div style="font-size: 14px; font-weight: bold; color: #ffffff; margin-top: 4px;">{item['judul']}</div>
                <div style="color: #94a3b8; font-size: 12px; margin-top: 3px;">📅 {item['tanggal']} | 💰 <span style="color: #34d399; font-weight: bold;">{item['harga']}</span></div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Cek Spesifikasi Detail", key=f"det_{item['id']}", use_container_width=True):
            st.session_state.selected_event_id = item['id']
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)


# -------------------- KOLOM KANAN: PANEL DETAIL / STRUK BARU (ATAS) & CHATBOX (BAWAH) --------------------
with kolom_kanan:
    
    # JIKA SUDAH BAYAR, PANEL ATAS BERUBAH MENJADI STRUK DIGITAL RESMI
    if st.session_state.pembayaran_sukses_data is not None:
        st.subheader("🎟️ Panel Struk Transaksi Terverifikasi")
        rcp = st.session_state.pembayaran_sukses_data
        
        st.markdown(f"""
            <div style="background-color: #1e293b; border: 2.5px solid #10b981; padding: 18px; border-radius: 8px; margin-bottom: 15px;">
                <div style="text-align: center; color: #10b981; font-weight: bold; font-size: 16px; margin-bottom: 10px;">🟢 TRANSAKSI SUKSES LUNAS 🟢</div>
                <h4 style="color: #ffffff; margin: 0 0 10px 0; font-size: 15px; border-bottom: 1px dashed rgba(255,255,255,0.2); padding-bottom: 5px; font-weight: bold;">STRUK RESMI DIGITAL</h4>
                <div style="font-size: 13px; color: #ffffff; line-height: 1.5;">
                    👤 <b>Nama Peserta:</b> {rcp['nama']}<br>
                    📧 <b>Email Aktif:</b> {rcp['email']}<br>
                    📞 <b>WhatsApp:</b> {rcp['wa']}<br><br>
                    📥 <b>Item Terdaftar:</b><br>
                    <span style="color: #38bdf8; font-weight: bold;">{rcp['summary_items']}</span>
                </div>
                <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.15); font-size: 15px; color: #10b981; font-weight: 900;">
                    TOTAL CASH SELESAI: Rp {rcp['total']:,}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader("📋 Log Detail Ringkasan Konten")
        evt = next((x for x in st.session_state.db_events if x['id'] == st.session_state.selected_event_id), None)
        if evt:
            badge_clr = "#10b981" if evt['harga_int'] == 0 else "#ef4444"
            st.markdown(f"""
                <div style="background-color: #1e293b; border: 2.5px solid #06b6d4; padding: 16px; border-radius: 8px; margin-bottom: 15px;">
                    <div style="font-size: 12px; font-weight: bold; color: {badge_clr}; margin-bottom: 5px;">{evt['status_label']} | {evt['category']} (KODE: {evt['id']})</div>
                    <h4 style="color: #ffffff; margin: 0 0 12px 0; font-size: 16px; font-weight: 800;">{evt['judul']}</h4>
                    <div style="font-size: 13px; line-height: 1.6; color: #ffffff;">
                        📌 <span style="color: #94a3b8;">Pembicara:</span> <b style="color:#ffffff;">{evt['pembicara']}</b><br>
                        📅 <span style="color: #94a3b8;">Waktu:</span> <b style="color:#ffffff;">{evt['tanggal']}</b><br>
                        💰 <span style="color: #94a3b8;">Investasi Tiket:</span> <span style="color: #f59e0b; font-weight: 900;">{evt['harga']}</span>
                    </div>
                    <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.15); font-size: 12.5px; color: #e2e8f0;">
                        <b style="color: #06b6d4;">Silabus:</b> {evt['deskripsi']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.write("---")
    
    # 2. PORTAL TRANSAKSI CHATBOX
    st.subheader("💬 Portal Transaksi Virtual")
    chat_box_area = st.container()
    
    with chat_box_area:
        for idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
                if "type" in msg and msg["type"] == "render_detail_inside_chat":
                    items_data = msg["data"]
                    st.markdown("<p style='color: #38bdf8; font-weight: bold; margin-bottom:4px;'>📋 KODE EVENT BERHASIL DI-LOAD:</p>", unsafe_allow_html=True)
                    for it in items_data:
                        st.markdown(f"<p style='color: #ffffff; margin:2px 0;'>• <b>[{it['id']}]</b> {it['judul']} ({it['harga']})</p>", unsafe_allow_html=True)
                
                if "type" in msg and msg["type"] == "render_invoice":
                    inv = msg["data"]
                    st.markdown(f"""
                    <div style="background-color: #2d3748; padding: 14px; border-radius: 6px; border: 1px solid #f59e0b; margin-top: 8px;">
                        <h4 style="color: #f59e0b; margin-top:0; font-weight:bold;">⚠️ NOTA INVOICE AUTOMATED GABUNGAN</h4>
                        <p style="color:#ffffff; margin-bottom:4px;"><b>Item Pendaftaran:</b></p>
                        <p style="color:#cbd5e1; font-size:13px; margin-bottom:10px;">{inv['summary_txt'].replace('- ', '• ')}</p>
                        <p style="color:#ffffff;"><b>TOTAL KESELURUHAN:</b> <span style="color:#ef4444; font-weight:bold; font-size:15px;">Rp {inv['total']:,}</span></p>
                        <p style="color:#94a3b8; font-size:11px; margin-top:5px;">Transfer Mandiri / BCA VA: <b>8839-0898-9825-34</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.reg_status == "waiting_payment":
                        if st.button("✅ Konfirmasi Saya Sudah Bayar Lunas", key=f"pay_confirm_{idx}", use_container_width=True):
                            items_terpilih = [x for x in st.session_state.db_events if x['id'] in st.session_state.cart_event_ids]
                            total_harga = sum(x['harga_int'] for x in items_terpilih)
                            summary_names = "<br>".join([f"- {x['judul']} ({x['harga']})" for x in items_terpilih])
                            
                            struk_gabungan = {
                                "nama": st.session_state.reg_data["nama"],
                                "email": st.session_state.reg_data["email"],
                                "wa": st.session_state.reg_data["wa"],
                                "summary_items": summary_names,
                                "total": total_harga
                            }
                            
                            st.session_state.pembayaran_sukses_data = struk_gabungan
                            st.session_state.messages.append({"role": "user", "content": "Saya sudah bayar kodenya."})
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "🎉 **Sistem Memvalidasi Pembayaran!** Status: LUNAS. Lembar bukti struk resmi digital berhasil dikirim dan ditampilkan di **Panel Bagian Atas** dashboard!"
                            })
                            st.session_state.reg_status = "idle"
                            st.rerun()

    # INPUT FIELD VIRTUAL CHATBOX (Menggunakan CSS kustom beralas Hijau Sage Soft)
    user_input = st.chat_input("Ketik kode nomor event di sini (misal: 1 atau 1,2)...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        if st.session_state.reg_status == "info_nama":
            st.session_state.reg_data["nama"] = user_input
            st.session_state.reg_status = "info_email"
            st.session_state.messages.append({"role": "assistant", "content": f"Nama tersimpan: **{user_input}**. Lanjut, ketikkan **Alamat Email** Anda:"})
            st.rerun()
            
        elif st.session_state.reg_status == "info_email":
            st.session_state.reg_data["email"] = user_input
            st.session_state.reg_status = "info_wa"
            st.session_state.messages.append({"role": "assistant", "content": "Email terekam. Terakhir, ketikkan **Nomor WhatsApp** aktif Anda:"})
            st.rerun()
            
        elif st.session_state.reg_status == "info_wa":
            st.session_state.reg_data["wa"] = user_input
            st.session_state.reg_status = "waiting_payment"
            
            items_terpilih = [x for x in st.session_state.db_events if x['id'] in st.session_state.cart_event_ids]
            total_harga = sum(x['harga_int'] for x in items_terpilih)
            summary_names = "\n".join([f"- {x['judul']} ({x['harga']})" for x in items_terpilih])
            
            if total_harga == 0:
                struk_gabungan = {
                    "nama": st.session_state.reg_data["nama"],
                    "email": st.session_state.reg_data["email"],
                    "wa": st.session_state.reg_data["wa"],
                    "summary_items": summary_names.replace('\n', '<br>'),
                    "total": 0
                }
                st.session_state.pembayaran_sukses_data = struk_gabungan
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "🎉 **Pendaftaran Berhasil!** Karena item pilihan Anda senilai Rp 0 (GRATIS), E-Struk Anda langsung diterbitkan secara instant di **Panel Bagian Atas!**"
                })
                st.session_state.reg_status = "idle"
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Data identitas lengkap. Berikut lembar invoice gabungan otomatis terhitung sistem:",
                    "type": "render_invoice",
                    "data": {
                        "summary_txt": summary_names,
                        "total": total_harga
                    }
                })
            st.rerun()
            
        else:
            user_text = user_input.lower()
            
            # 1. Cek apakah ada angka (ID Event) untuk pendaftaran otomatis
            list_angka = [int(s) for s in re.findall(r'\d+', user_input)]
            valid_items = [x for x in st.session_state.db_events if x['id'] in list_angka]
            
            if valid_items:
                st.session_state.pembayaran_sukses_data = None  # Reset struk lama jika memesan ulang
                st.session_state.cart_event_ids = [x['id'] for x in valid_items]
                st.session_state.selected_event_id = valid_items[0]['id']
                st.session_state.reg_status = "info_nama"
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "⚙️ **Sistem Berhasil Meload Kode Event Pilihan Anda:**",
                    "type": "render_detail_inside_chat",
                    "data": valid_items
                })
                st.session_state.messages.append({"role": "assistant", "content": "Mohon masukkan **Nama Lengkap Anda** pada kolom chat untuk memulai registrasi form:"})
            
            # 2. Logika Keyword Pintar jika tidak ada angka (Filter Otomatis)
            elif any(kw in user_text for kw in ["gratis", "free", "0"]):
                st.session_state.filter_harga = "Gratis"
                st.session_state.messages.append({"role": "assistant", "content": "Tentu! Saya telah memfilter daftar untuk menampilkan **Event Gratis**. Silakan cek daftar di kolom kiri."})
            
            elif any(kw in user_text for kw in ["semua", "list", "daftar", "apa saja"]):
                st.session_state.filter_harga = "Semua"
                st.session_state.messages.append({"role": "assistant", "content": "Menampilkan **Semua Event** yang tersedia. Silakan pilih nomor kode yang Anda inginkan."})
                
            elif "workshop" in user_text:
                st.session_state.messages.append({"role": "assistant", "content": "Kami memiliki beberapa **Workshop** menarik. Silakan lihat kode nomor di daftar sebelah kiri untuk mendaftar."})
            
            elif any(kw in user_text for kw in ["lomba", "hackathon", "kompetisi"]):
                st.session_state.messages.append({"role": "assistant", "content": "Ingin berkompetisi? Cek kategori **Lomba** di daftar sebelah kiri untuk kode pendaftarannya."})
                
            else:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "Maaf, saya belum menemukan kode tersebut atau instruksi tidak dikenal. Silakan ketik **Nomor Kode** (misal: 1) atau kata kunci seperti **'Gratis'**."
                })
            st.rerun()