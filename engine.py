import re

class EventChatbotEngine:
    def __init__(self):
        # Database Paket Event & Konferensi
        self.menu_data = {
            "seminar": {
                "price": 150000,
                "emoji": "🎤",
                "desc": "Seminar 1 hari, termasuk materi & sertifikat",
                "capacity": 200
            },
            "workshop": {
                "price": 350000,
                "emoji": "🛠️",
                "desc": "Workshop intensif 2 hari, praktek langsung",
                "capacity": 50
            },
            "konferensi": {
                "price": 500000,
                "emoji": "🏛️",
                "desc": "Konferensi internasional 3 hari, full-board",
                "capacity": 500
            },
            "webinar": {
                "price": 75000,
                "emoji": "💻",
                "desc": "Webinar online via Zoom, akses rekaman selamanya",
                "capacity": 1000
            },
            "gala_dinner": {
                "price": 250000,
                "emoji": "🍽️",
                "desc": "Malam gala dinner networking eksklusif",
                "capacity": 100
            },
            "bootcamp": {
                "price": 750000,
                "emoji": "🚀",
                "desc": "Bootcamp intensif 5 hari, proyek nyata",
                "capacity": 30
            },
        }

        # Alias: variasi nama yang mungkin diketik user
        self.aliases = {
            "seminar": ["seminar"],
            "workshop": ["workshop", "ws"],
            "konferensi": ["konferensi", "conference", "konfrensi"],
            "webinar": ["webinar", "online", "zoom"],
            "gala_dinner": ["gala", "dinner", "gala dinner", "gala_dinner"],
            "bootcamp": ["bootcamp", "boot camp", "boot"],
        }

        # Bangun reverse map: alias -> key
        self._alias_map = {}
        for key, aliases in self.aliases.items():
            for alias in aliases:
                self._alias_map[alias] = key

        # Regex Patterns
        self.re_number = r"\b(\d+)\b"
        all_aliases = [re.escape(a) for a in sorted(self._alias_map.keys(), key=len, reverse=True)]
        self.re_menu = r"\b(" + "|".join(all_aliases) + r")\b"
        self.re_split = r"[,.]|\bdan\b|\b&\b"

        # Regex untuk pembatalan/pengurangan
        self.re_cancel_all = r"\b(batalkan semua|hapus semua|reset|kosongkan|batal semua)\b"
        self.re_reduce = r"\b(batalkan|kurangi|tidak jadi|hapus|cancel|remove)\b"

    def _normalize_key(self, raw):
        """Ubah alias menjadi key utama"""
        return self._alias_map.get(raw.lower(), raw.lower())

    def _parse_single_segment(self, text):
        """Helper untuk memproses satu segmen kalimat"""
        text = text.lower().strip()

        item_match = re.search(self.re_menu, text)
        if not item_match:
            return None

        raw_item = item_match.group(1)
        item_key = self._normalize_key(raw_item)

        if item_key not in self.menu_data:
            return None

        qty_match = re.search(self.re_number, text)
        qty = int(qty_match.group(1)) if qty_match else 1

        return {
            "item": item_key,
            "qty": qty,
            "price": self.menu_data[item_key]["price"],
            "emoji": self.menu_data[item_key]["emoji"],
        }

    def process_message(self, message):
        """Method utama untuk memproses input user"""
        results = []
        segments = re.split(self.re_split, message.lower())

        for segment in segments:
            parsed = self._parse_single_segment(segment)
            if parsed:
                if re.search(self.re_reduce, segment):
                    parsed["action"] = "remove"
                else:
                    parsed["action"] = "add"
                results.append(parsed)

        return results

    def update_cart(self, current_cart, parsed_items):
        """Update keranjang berdasarkan hasil parse"""
        for item in parsed_items:
            key = item["item"]
            qty = item["qty"]
            action = item["action"]

            if action == "add":
                current_cart[key] = current_cart.get(key, 0) + qty
            elif action == "remove":
                if key in current_cart:
                    current_cart[key] = max(0, current_cart[key] - qty)
                    if current_cart[key] == 0:
                        del current_cart[key]

        return current_cart

    def detect_intent(self, text):
        text = text.lower()
        if re.search(r"\b(reset|ulang)\b", text):
            return "RESET"
        if re.search(self.re_cancel_all, text):
            return "CANCEL_ALL"
        if re.search(self.re_reduce, text):
            return "REDUCE_ITEM"
        if re.search(r"\b(menu|paket|apa saja|list|event apa|acara)\b|lihat daftar|tampilkan daftar", text):
            return "ASK_MENU"
        if re.search(r"\b(selesai|bayar|checkout|konfirmasi|lanjut|pesan sekarang)\b", text):
            return "CHECKOUT"
        if re.search(r"\b(ya|yes|oke|ok|betul|siap|baik|setuju|lanjutkan)\b", text):
            return "YES"
        if re.search(r"\b(tidak|enggak|batal|no|salah|cancel)\b", text):
            return "NO"
        return "UNKNOWN"
