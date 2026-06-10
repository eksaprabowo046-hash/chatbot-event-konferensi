import streamlit as st
import pandas as pd
from event_fsm import EventFSM, FSM

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="EventPro Bot",
    page_icon="🎪",
    layout="wide",
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main App Background */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Chat Bubble Styling */
    .stChatMessage {
        background-color: transparent !important;
        padding: 0px !important;
    }

    [data-testid="chatAvatarIcon-user"] {
        background-color: #6C63FF !important;
    }

    [data-testid="chatAvatarIcon-assistant"] {
        background-color: #1e1e2f !important;
    }

    /* Professional Cards inside Chat */
    .chat-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-top: 10px;
    }

    .stMetric {
        background: #F1F5F9;
        padding: 10px;
        border-radius: 10px;
    }

    /* Hide unnecessary Streamlit UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Chat Input Styling */
    .stChatInputContainer {
        padding-bottom: 20px !important;
    }
    
    .metric-container {
        display: flex;
        gap: 20px;
        overflow-x: auto;
        padding: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- BOT INITIALIZATION ---
if "bot" not in st.session_state:
    st.session_state.bot = FSM()
    st.session_state.bot.step()
    st.session_state.history = [
        {"role": "assistant", "content": st.session_state.bot.get_response(), "id": "init"}
    ]
if "registrants" not in st.session_state:
    st.session_state.registrants = []

# --- SIDEBAR (Minimalis) ---
with st.sidebar:
    st.markdown("<h2 style='color: white;'>🎪 EventPro</h2>", unsafe_allow_html=True)
    st.caption("Premium Concierge v2.5")
    st.divider()
    
    st.write("### 👤 Status User")
    if st.session_state.registrants:
        st.success(f"Terdaftar sebagai: {st.session_state.registrants[-1]['name']}")
    else:
        st.warning("Belum melengkapi profil.")

    if st.button("♻️ Reset Percakapan", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- MAIN UI (ONE CHAT INTERFACE) ---
st.markdown("<h1 style='text-align: center; color: #1E293B; margin-bottom: 30px;'>Concierge Event Premium</h1>", unsafe_allow_html=True)

# Menampilkan Riwayat Chat
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Render UI Spesifik berdasarkan konten pesan (Rich Response)
        if "Katalog Event Eksklusif" in msg["content"]:
            # Tampilkan Grid Event langsung di bawah bubble chat
            menu_items = st.session_state.bot.nlp.menu_data
            cols = st.columns(2)
            for idx, (key, data) in enumerate(menu_items.items()):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="chat-card">
                        <span style="background:#EEF2FF; color:#6366F1; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:bold;">{data['status'].upper()}</span>
                        <h4 style="margin:10px 0 5px 0;">{data['emoji']} {key.replace('_',' ').title()}</h4>
                        <p style="font-size:12px; color:#64748B;">{data['desc']}</p>
                        <b style="color:#1E293B;">Rp {data['price']:,}</b>
                    </div>
                    """, unsafe_allow_html=True)

        if "Berhasil Dikonfirmasi" in msg["content"]:
            # Tampilkan Form Pendaftaran langsung di alur chat jika sudah checkout
            with st.container():
                with st.form(key=f"form_{msg.get('id', 'default')}"):
                    name = st.text_input("Nama Lengkap")
                    email = st.text_input("Email")
                    submitted = st.form_submit_button("Simpan Data")
                    if submitted:
                        st.session_state.registrants.append({"name": name, "email": email})
                        st.toast("Data disimpan!", icon="✅")

        if "dashboard" in msg["content"].lower() or "statistik" in msg["content"].lower():
            # Render Dashboard Stats di dalam Chat
            with st.container():
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Event", "6", "Aktif")
                c2.metric("Pendaftar", f"{len(st.session_state.registrants)}", "+5%")
                c3.metric("Uptime", "99.9%", "Premium")
                
                # Mini Chart untuk estetika dashboard
                chart_data = pd.DataFrame({
                    'Hari': ['Sen', 'Sel', 'Rab', 'Kam', 'Jum'],
                    'Trafik': [20, 45, 30, 80, 50]
                })
                st.area_chart(chart_data.set_index('Hari'), height=150, color="#6C63FF")

# Chat Input
if prompt := st.chat_input("Tanyakan paket, status acara, atau ketik 'dashboard'..."):
    import time
    msg_id = str(time.time())
    # Tambah chat user ke history
    st.session_state.history.append({"role": "user", "content": prompt, "id": msg_id})
    
    # Proses logika via FSM
    st.session_state.bot.step(prompt)
    bot_reply = st.session_state.bot.get_response()
    
    # Tambah chat bot ke history
    st.session_state.history.append({"role": "assistant", "content": bot_reply, "id": msg_id + "_bot"})
    
    st.rerun()
