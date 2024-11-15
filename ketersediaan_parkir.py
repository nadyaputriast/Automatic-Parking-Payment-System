class KetersediaanParkir:
    def __init__(self):
        self.slots = {
            'motor': [f'A{i}' for i in range(1, 101)],   # A1 - A100 untuk motor
            'mobil': [f'B{i}' for i in range(1, 51)],    # B1 - B50 untuk mobil
            'box': [f'C{i}' for i in range(1, 21)],      # C1 - C20 untuk kendaraan box
            'truk': [f'D{i}' for i in range(1, 11)],     # D1 - D10 untuk truk
            'bus': [f'E{i}' for i in range(1, 6)]        # E1 - E5 untuk bus
        }
        self.terisi = {key: [] for key in self.slots}  # Daftar slot yang sedang digunakan
        
        # Untuk nampilin harga tiap kendaraan
        self.harga = {
            'motor': 2000,
            'mobil': 3000,
            'box': 5000,
            'truk': 10000,
            'bus': 30000
        }
        
    def cek_ketersediaan(self, jenis_kendaraan):
        return bool(self.slots[jenis_kendaraan])
    
    def alokasikan_slot(self, jenis_kendaraan):
        """Alokasikan slot parkir untuk kendaraan yang masuk."""
        if self.cek_ketersediaan(jenis_kendaraan):
            slot = self.slots[jenis_kendaraan].pop(0)  # Ambil slot pertama yang tersedia
            self.terisi[jenis_kendaraan].append(slot)  # Tandai slot sebagai terisi
            print(f"Slot {slot} dialokasikan untuk {jenis_kendaraan}.")
            return slot
        else:
            print(f"Tidak ada slot parkir tersedia untuk {jenis_kendaraan}.")
            return None

    def kosongkan_slot(self, jenis_kendaraan, slot):
        """Kosongkan slot parkir ketika kendaraan keluar."""
        if slot in self.terisi[jenis_kendaraan]:
            self.terisi[jenis_kendaraan].remove(slot)  # Hapus dari daftar terisi
            self.slots[jenis_kendaraan].append(slot)  # Tambahkan kembali ke daftar slot kosong
            print(f"Slot {slot} telah dikosongkan untuk {jenis_kendaraan}.")
        else:
            print(f"Slot {slot} tidak ditemukan sebagai terisi untuk {jenis_kendaraan}.")
            
    def hitung_biaya(self, jenis_kendaraan, jumlah_hari):
        """Hitung biaya parkir berdasarkan jenis kendaraan dan jumlah hari."""
        if jenis_kendaraan in self.harga:
            return self.harga[jenis_kendaraan] * jumlah_hari
        else:
            print(f"Tidak ada harga untuk jenis kendaraan {jenis_kendaraan}.")
            return 0