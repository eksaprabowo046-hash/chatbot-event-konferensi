import streamlit as st
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
    /* Warna aksen tema event */
    :root {
        --accent: #6C63FF;
    }

    /* Kartu keranjang */
    .cart-item {
        background: #f8f7ff;
        border-left: 4px solid #6C63FF;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 8px;
    }

    /* Metric box */
    [data-testid="stMetric"] {
        background-color: #eeeaff;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #c4beff;
    }

    /* Chat container */
    .stChatMessage { padding: 10px; }

    /* Header gradient */
    .main-header {
        background: linear-gradient(135deg, #6C63FF 0%, #3EC6E0 100%);
        padding: 20px 28px;
        border-radius: 14px;
        margin-bottom: 10px;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 2rem; color: white; }
    .main-header p  { margin: 4px 0 0 0; opacity: 0.9; font-size: 1rem; }

    /* Card menu */
    .menu-card {
        background: white;
        border: 1px solid #e2e0ff;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(108,99,255,0.07);
        transition: box-shadow 0.2s;
    }
    .menu-card:hover { box-shadow: 0 4px 16px rgba(108,99,255,0.15); }

    /* Badge kapasitas */
    .badge {
        display: inline-block;
        background: #eeeaff;
        color: #6C63FF;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- BOT INITIALIZATION ---
if "bot" not in st.session_state:
    st.session_state.bot = EventFSM()
    st.session_state.bot.step()
    st.session_state.history = [
        {"role": "assistant", "content": st.session_state.bot.get_response()}
    ]

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🎪 EventPro — Sistem Registrasi Event & Konferensi</h1>
    <p>Chatbot cerdas berbasis FSA untuk pendaftaran seminar, workshop, konferensi, dan lebih banyak lagi.</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# --- MAIN LAYOUT WITH TABS ---
tab1, tab2 = st.tabs(["💬 Registrasi Event", "📋 Katalog Event"])

# =====================================================================
# TAB 1 — CHATBOT REGISTRASI
# =====================================================================
with tab1:
    col_chat, col_info = st.columns([2, 1])

    # ---- KOLOM INFO / KERANJANG ----
    with col_info:
        st.subheader("🛒 Keranjang Pendaftaran")

        if st.session_state.bot.cart:
            total = 0
            for i, item in enumerate(st.session_state.bot.cart):
                subtotal = item["price"] * item["qty"]
                total += subtotal
                display_name = item["item"].replace("_", " ").title()
                st.markdown(
                    f'<div class="cart-item">'
                    f'<b>{i+1}. {item["emoji"]} {display_name}</b><br>'
                    f'<small>{item["qty"]} tiket × Rp {item["price"]:,} = <b>Rp {subtotal:,}</b></small>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.divider()
            st.metric("💰 Total Pembayaran", f"Rp {total:,}")

            if st.button("🗑️ Kosongkan Keranjang", use_container_width=True):
                st.session_state.bot.cart = []
                st.rerun()
        else:
            st.info("Keranjang masih kosong.\nMulai pilih event di kolom chat!")

        st.markdown("---")

        # Status & kontrol
        state_colors = {
            "REGISTERING": "🟢",
            "CONFIRMING": "🟡",
            "COMPLETED": "🔵",
        }
        state_name = st.session_state.bot.state.name
        st.caption(f"Status Bot: {state_colors.get(state_name, '⚪')} `{state_name}`")

        if st.button("♻️ Reset Sistem", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.markdown("---")
        st.markdown("**💡 Contoh Perintah:**")
        st.markdown("""
- `paket` — lihat daftar event
- `daftar 1 konferensi`
- `daftar 2 webinar dan 1 workshop`
- `batalkan 1 webinar`
- `checkout` / `bayar` — lanjut pembayaran
- `reset` — mulai ulang
""")

    # ---- KOLOM CHAT ----
    with col_chat:
        chat_container = st.container(height=500)

        with chat_container:
            for msg in st.session_state.history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Contoh: daftar 2 workshop dan 1 webinar..."):
            st.session_state.history.append({"role": "user", "content": prompt})

            st.session_state.bot.step(prompt)
            bot_reply = st.session_state.bot.get_response()

            st.session_state.history.append({"role": "assistant", "content": bot_reply})
            st.rerun()

# =====================================================================
# TAB 2 — KATALOG EVENT
# =====================================================================
with tab2:
    st.header("📋 Katalog Paket Event & Konferensi")
    st.markdown(
        "Temukan event yang sesuai kebutuhan Anda. "
        "Semua paket sudah termasuk sertifikat keikutsertaan resmi."
    )
    st.markdown("---")

    menu_items = st.session_state.bot.nlp.menu_data

    cols = st.columns(2)
    for index, (key, data) in enumerate(menu_items.items()):
        with cols[index % 2]:
            display_name = key.replace("_", " ").title()
            st.markdown(
                f'<div class="menu-card">'
                f'<h3 style="margin:0 0 6px 0">{data["emoji"]} {display_name}</h3>'
                f'<p style="margin:0 0 10px 0;color:#555">{data["desc"]}</p>'
                f'<span class="badge">👥 Kapasitas: {data["capacity"]} peserta</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.metric(label="Harga per Tiket", value=f"Rp {data['price']:,}")
            st.markdown("")
