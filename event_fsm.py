from enum import Enum
from engine import EventChatbotEngine


class BotState(Enum):
    REGISTERING = "REGISTERING"
    CONFIRMING = "CONFIRMING"
    COMPLETED = "COMPLETED"


class EventFSM:
    def __init__(self):
        self.nlp = EventChatbotEngine()
        self.state = BotState.REGISTERING
        self.cart_dict = {}  # Format: {item_key: qty}
        self.response = ""

    @property
    def cart(self):
        """Mengembalikan isi keranjang dalam format List[Dict]"""
        cart_list = []
        for key, qty in self.cart_dict.items():
            if key in self.nlp.menu_data:
                item_data = self.nlp.menu_data[key]
                cart_list.append({
                    "item": key,
                    "qty": qty,
                    "price": item_data["price"],
                    "emoji": item_data["emoji"],
                })
        return cart_list

    @cart.setter
    def cart(self, value):
        if isinstance(value, list) and len(value) == 0:
            self.cart_dict = {}
        elif isinstance(value, dict):
            self.cart_dict = value

    def get_response(self):
        return self.response

    def step(self, prompt=None):
        """Menjalankan satu langkah transisi state di FSM."""
        if prompt is None:
            self.state = BotState.REGISTERING
            self.response = (
                "Selamat datang di layanan reservasi **EventPro Premium** 🎉\n\n"
                "Saya adalah asisten virtual Anda yang akan memandu proses pendaftaran event dan konferensi eksklusif kami.\n\n"
                "Bagaimana saya bisa membantu Anda hari ini? Anda dapat mengetikkan **'paket'** untuk melihat katalog kami atau menanyakan status acara tertentu."
            )
            return

        prompt_clean = prompt.strip()
        if not prompt_clean:
            self.response = "Ada yang bisa saya bantu? Ketik **'paket'** untuk melihat daftar event."
            return

        # --- TRANSISI STATE ---
        if self.state == BotState.REGISTERING:
            intent = self.nlp.detect_intent(prompt_clean)

            if intent == "RESET":
                self.cart_dict = {}
                self.state = BotState.REGISTERING
                self.response = (
                    "Tentu, saya telah mereset sesi pendaftaran Anda. ♻️\n"
                    "Mari kita mulai kembali dari awal. Ada paket event yang ingin Anda jelajahi?"
                )

            elif intent == "CANCEL_ALL":
                self.cart_dict = {}
                self.response = "Baik, saya telah mengosongkan keranjang pendaftaran Anda. Apakah ada kategori acara lain yang menarik perhatian Anda?"

            elif intent == "ASK_ONGOING":
                ongoing = [v for k, v in self.nlp.menu_data.items() if v['status'] == 'berlangsung']
                lines = ["🌟 **Berikut adalah daftar acara yang sedang atau akan segera berlangsung:**\n"]
                for item in ongoing:
                    lines.append(f"- {item['emoji']} **{item['desc'].split(',')[0]}** ({item['date']})")
                lines.append("\nApakah ada salah satu dari acara di atas yang ingin Anda ikuti?")
                self.response = "\n".join(lines)

            elif intent == "ASK_PAST":
                past = [v for k, v in self.nlp.menu_data.items() if v['status'] == 'terlaksana']
                lines = ["📚 **Acara-acara menarik yang telah sukses kami laksanakan:**\n"]
                for item in past:
                    lines.append(f"- {item['emoji']} **{item['desc'].split(',')[0]}** (Selesai pada {item['date']})")
                lines.append("\nNantikan kembali kehadiran acara-acara serupa di masa mendatang!")
                self.response = "\n".join(lines)

            elif intent == "ASK_MENU":
                lines = ["Tentu, ini adalah **Katalog Event Eksklusif** kami saat ini:\n"]
                for key, val in self.nlp.menu_data.items():
                    lines.append(
                        f"- {val['emoji']} **{key.replace('_', ' ').title()}** "
                        f"— Rp {val['price']:,} | Kapasitas: {val['capacity']} peserta\n"
                        f"  _{val['desc']}_"
                    )
                lines.append("\nSilakan sebutkan nama event dan jumlah tiket yang Anda inginkan, misalnya: *'Daftar 2 tiket konferensi'*")
                self.response = "\n".join(lines)

            elif intent == "CHECKOUT":
                if not self.cart_dict:
                    self.response = "Mohon maaf, sepertinya Anda belum memilih event. Bolehkah saya membantu Anda memilih salah satu paket yang tersedia?"
                else:
                    self.state = BotState.CONFIRMING
                    lines = ["📋 **Berikut adalah Ringkasan Reservasi Anda:**\n"]
                    total = 0
                    for i, (key, qty) in enumerate(self.cart_dict.items()):
                        val = self.nlp.menu_data[key]
                        subtotal = val["price"] * qty
                        total += subtotal
                        lines.append(
                            f"**{val['emoji']} {key.replace('_', ' ').title()}** "
                            f"({qty} tiket) = Rp {subtotal:,}"
                        )
                    lines.append(f"\n💰 **Total Pembayaran: Rp {total:,}**")
                    lines.append(
                        "\nApakah data pendaftaran sudah benar? "
                        "(Ketik **'ya'** untuk konfirmasi, **'tidak'** untuk membatalkan)"
                    )
                    self.response = "\n".join(lines)

            else:
                parsed_items = self.nlp.process_message(prompt_clean)
                if parsed_items:
                    self.cart_dict = self.nlp.update_cart(self.cart_dict, parsed_items)
                    added = [p for p in parsed_items if p["action"] == "add"]
                    removed = [p for p in parsed_items if p["action"] == "remove"]

                    msgs = []
                    for p in added:
                        name = p["item"].replace("_", " ").title()
                        msgs.append(f"✅ Baik, **{p['qty']} tiket {name}** telah saya tambahkan ke daftar Anda.")
                    for p in removed:
                        name = p["item"].replace("_", " ").title()
                        msgs.append(f"🗑️ Tentu, **{p['qty']} tiket {name}** telah saya hapus dari daftar.")

                    msgs.append("\nApakah masih ada event lain yang ingin Anda tambahkan, atau kita bisa lanjut ke tahap konfirmasi?")
                    self.response = "\n".join(msgs)
                else:
                    self.response = (
                        "Mohon maaf, saya kurang memahami permintaan tersebut. 🤔\n"
                        "Bisa tolong diulangi? Anda bisa menanyakan daftar 'paket' atau langsung menyebutkan nama event yang diinginkan."
                    )

        elif self.state == BotState.CONFIRMING:
            intent = self.nlp.detect_intent(prompt_clean)
            prompt_lower = prompt_clean.lower()

            if intent == "YES" or prompt_lower in ["ya", "yes", "oke", "ok", "betul", "siap", "setuju", "lanjutkan"]:
                self.state = BotState.COMPLETED
                total = sum(
                    self.nlp.menu_data[k]["price"] * q for k, q in self.cart_dict.items()
                )
                items_str = ", ".join(
                    f"{self.nlp.menu_data[k]['emoji']} {k.replace('_', ' ').title()} ({q}x)"
                    for k, q in self.cart_dict.items()
                )
                self.response = (
                    f"🎉 **Reservasi Anda Telah Berhasil Dikonfirmasi!**\n\n"
                    f"Terima kasih telah mempercayakan pengalaman belajar Anda kepada kami.\n"
                    f"📌 **Detail Event:** {items_str}\n"
                    f"💰 **Total Pembayaran:** **Rp {total:,}**\n\n"
                    f"Mohon lengkapi data diri Anda pada form yang tersedia. Instruksi pembayaran dan E-tiket akan segera kami kirimkan melalui email resmi. ✉️"
                )

            elif intent == "NO" or prompt_lower in ["tidak", "no", "batal", "salah", "enggak", "cancel"]:
                self.state = BotState.REGISTERING
                self.response = (
                    "Baik, pendaftaran telah saya tunda.\n"
                    "Silakan tinjau kembali pilihan Anda atau tanyakan paket lain jika ada yang lebih sesuai."
                )

            else:
                self.response = (
                    "Mohon jawab dengan **'ya'** untuk konfirmasi, atau **'tidak'** untuk membatalkan."
                )

        elif self.state == BotState.COMPLETED:
            self.cart_dict = {}
            self.state = BotState.REGISTERING
            self.step(prompt_clean)


# Alias untuk kompatibilitas
FSM = EventFSM
