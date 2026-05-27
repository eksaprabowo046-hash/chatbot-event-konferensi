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
                "Selamat datang di **EventPro Bot** 🎉\n\n"
                "Saya siap membantu Anda mendaftar ke event & konferensi pilihan.\n"
                "Ketik **'paket'** untuk melihat daftar event yang tersedia, "
                "atau langsung ketik nama event yang ingin Anda ikuti!"
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
                    "Sistem telah direset. ♻️\n"
                    "Silakan mulai pendaftaran baru! Ketik **'paket'** untuk melihat pilihan event."
                )

            elif intent == "CANCEL_ALL":
                self.cart_dict = {}
                self.response = "🗑️ Semua pilihan event telah dihapus dari keranjang. Mau mendaftar event lain?"

            elif intent == "ASK_MENU":
                lines = ["Berikut adalah **daftar paket event** yang tersedia:\n"]
                for key, val in self.nlp.menu_data.items():
                    lines.append(
                        f"- {val['emoji']} **{key.replace('_', ' ').title()}** "
                        f"— Rp {val['price']:,} | Kapasitas: {val['capacity']} peserta\n"
                        f"  _{val['desc']}_"
                    )
                lines.append("\nSilakan ketik nama event untuk mendaftar, contoh: *'daftar 2 workshop'*")
                self.response = "\n".join(lines)

            elif intent == "CHECKOUT":
                if not self.cart_dict:
                    self.response = "❗ Anda belum memilih event apapun. Ketik **'paket'** untuk melihat daftar event."
                else:
                    self.state = BotState.CONFIRMING
                    lines = ["📋 **Ringkasan Pendaftaran Anda:**\n"]
                    total = 0
                    for i, (key, qty) in enumerate(self.cart_dict.items()):
                        val = self.nlp.menu_data[key]
                        subtotal = val["price"] * qty
                        total += subtotal
                        lines.append(
                            f"**{i+1}. {val['emoji']} {key.replace('_', ' ').title()}** "
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
                        msgs.append(f"✅ **{p['qty']} tiket {name}** berhasil ditambahkan.")
                    for p in removed:
                        name = p["item"].replace("_", " ").title()
                        msgs.append(f"🗑️ **{p['qty']} tiket {name}** berhasil dihapus.")

                    msgs.append("Ada lagi? Ketik **'checkout'** / **'bayar'** untuk melanjutkan pembayaran.")
                    self.response = "\n".join(msgs)
                else:
                    self.response = (
                        "Maaf, saya tidak mengerti. 🤔\n"
                        "Ketik **'paket'** untuk melihat daftar event, "
                        "atau contoh: *'daftar 1 konferensi dan 2 webinar'*"
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
                    f"🎉 **Pendaftaran Berhasil! Selamat bergabung!**\n\n"
                    f"📌 Event yang didaftarkan: {items_str}\n"
                    f"💰 Total yang harus dibayar: **Rp {total:,}**\n\n"
                    f"Silakan lakukan pembayaran di loket atau transfer ke rekening resmi kami.\n"
                    f"E-tiket akan dikirimkan ke email Anda dalam 1x24 jam. ✉️"
                )

            elif intent == "NO" or prompt_lower in ["tidak", "no", "batal", "salah", "enggak", "cancel"]:
                self.state = BotState.REGISTERING
                self.response = (
                    "❌ Pendaftaran dibatalkan.\n"
                    "Anda dapat mengedit pilihan event atau ketik **'paket'** untuk memulai ulang."
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
