class KetersediaanParkir:
    def __init__(self):
        self.slots = {
            'motor': [f'A{i}' for i in range(1, 101)],   # 100 slot untuk motor
            'mobil': [f'B{i}' for i in range(1, 51)],    # 50 slot untuk mobil
            'box': [f'C{i}' for i in range(1, 21)],      # 20 slot untuk box
            'truk': [f'D{i}' for i in range(1, 11)],     # 10 slot untuk truk
            'bus': [f'E{i}' for i in range(1, 6)]        # 5 slot untuk bus
        }
        self.terisi = {key: [] for key in self.slots}  # Slot yang terisi untuk tiap jenis kendaraan
        self.slot_state = {slot: 'AVAILABLE' for sublist in self.slots.values() for slot in sublist}
        
        self.harga = {
            'motor': 2000,     # Harga per hari
            'mobil': 3000,     # Harga per hari
            'box': 5000,       # Harga per hari
            'truk': 10000,     # Harga per hari
            'bus': 30000       # Harga per hari
        }

    def cek_ketersediaan(self, jenis_kendaraan):
        """
        Memeriksa ketersediaan slot untuk jenis kendaraan tertentu.
        
        :param jenis_kendaraan: Jenis kendaraan ('motor', 'mobil', 'box', 'truk', 'bus')
        :return: Boolean, True jika ada slot tersedia
        """
        available_slots = [slot for slot in self.slots[jenis_kendaraan] if self.slot_state[slot] == 'AVAILABLE']
        return len(available_slots) > 0

    def alokasikan_slot(self, jenis_kendaraan):
        """
        Mencari dan mengalokasikan slot untuk jenis kendaraan tertentu.
        
        :param jenis_kendaraan: Jenis kendaraan ('motor', 'mobil', 'box', 'truk', 'bus')
        :return: Nomor slot yang dialokasikan atau None jika tidak tersedia
        """
        if self.cek_ketersediaan(jenis_kendaraan):
            # Cari slot pertama yang AVAILABLE
            slot = next(slot for slot in self.slots[jenis_kendaraan] if self.slot_state[slot] == 'AVAILABLE')
            
            # Alokasikan slot
            self.slot_state[slot] = 'ALLOCATED'       # Ubah state slot menjadi ALLOCATED
            self.terisi[jenis_kendaraan].append(slot)  # Tambahkan ke daftar terisi
            print(f"Slot {slot} telah dialokasikan untuk {jenis_kendaraan}.")
            return slot
        else:
            print(f"Tidak ada slot parkir tersedia untuk {jenis_kendaraan}.")
            return None

    def kosongkan_slot(self, jenis_kendaraan, slot):
        """
        Mengosongkan slot parkir untuk jenis kendaraan tertentu.
        
        :param jenis_kendaraan: Jenis kendaraan ('motor', 'mobil', 'box', 'truk', 'bus')
        :param slot: Nomor slot yang akan dikosongkan
        """
        if slot in self.terisi[jenis_kendaraan]:
            self.terisi[jenis_kendaraan].remove(slot)  # Hapus dari daftar terisi
            self.slot_state[slot] = 'AVAILABLE'       # Ubah state slot menjadi AVAILABLE
            print(f"Slot {slot} untuk {jenis_kendaraan} telah dikosongkan.")
        else:
            print(f"Slot {slot} tidak ditemukan di daftar terisi untuk {jenis_kendaraan}.")

    def hitung_biaya(self, jenis_kendaraan, durasi):
        """
        Menghitung biaya parkir berdasarkan jenis kendaraan dan durasi.
        
        :param jenis_kendaraan: Jenis kendaraan ('motor', 'mobil', 'box', 'truk', 'bus')
        :param durasi: Durasi parkir dalam hari
        :return: Total biaya parkir
        """
        # Validasi jenis kendaraan
        if jenis_kendaraan not in self.harga:
            raise ValueError(f"Jenis kendaraan {jenis_kendaraan} tidak dikenali")
        
        # Minimal biaya adalah 1 hari penuh
        durasi = max(1, durasi)
        
        # Hitung total biaya 
        total_biaya = self.harga[jenis_kendaraan] * durasi
        return total_biaya

    def tampilkan_ketersediaan(self):
        """
        Menampilkan ketersediaan slot parkir untuk semua jenis kendaraan.
        Format tampilannya adalah 'total_slot/tersedia' yang dimulai dengan 'total_slot/0'.
        """
        print("Ketersediaan Slot Parkir:")
        for jenis, slot_list in self.slots.items():
            total_slot = len(slot_list)
            terisi = len(self.terisi[jenis])  # Nilai terisi
            tersedia = total_slot - terisi  # Slot yang tersedia (total - terisi)
            print(f"{jenis.capitalize()}: {tersedia}/{total_slot} tersedia.")