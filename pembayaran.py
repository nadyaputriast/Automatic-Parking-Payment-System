from plat_kendaraan import PlatKendaraan
from datetime import datetime

class Pembayaran:
    states = ['idle', 'validating', 'calculating_payment', 'processing_payment', 'payment_completed', 'error']

    def __init__(self, plat_kendaraan):
        self.plat_kendaraan = plat_kendaraan
        self.data_kendaraan = None
        self.biaya = 0
        self.state = 'idle'  # Inisialisasi state awal

    def start_payment(self):
        """Transisi dari 'idle' ke 'validating'"""
        if self.state == 'idle':
            self.state = 'validating'
        else:
            print("Transisi tidak valid.")

    def validate_success(self):
        """Transisi dari 'validating' ke 'calculating_payment'"""
        if self.state == 'validating':
            self.state = 'calculating_payment'
        else:
            print("Transisi tidak valid.")

    def validate_failed(self):
        """Transisi dari 'validating' ke 'error'"""
        if self.state == 'validating':
            self.state = 'error'
        else:
            print("Transisi tidak valid.")

    def calculate(self):
        """Transisi dari 'calculating_payment' ke 'processing_payment'"""
        if self.state == 'calculating_payment':
            self.state = 'processing_payment'
        else:
            print("Transisi tidak valid.")

    def process_success(self):
        """Transisi dari 'processing_payment' ke 'payment_completed'"""
        if self.state == 'processing_payment':
            self.state = 'payment_completed'
        else:
            print("Transisi tidak valid.")

    def process_failed(self):
        """Transisi dari 'processing_payment' ke 'error'"""
        if self.state == 'processing_payment':
            self.state = 'error'
        else:
            print("Transisi tidak valid.")

    def reset(self):
        """Reset state ke 'idle'"""
        self.state = 'idle'

    def validate_kendaraan(self, nomor_plat, kode_unik=None):
        """Validasi data kendaraan berdasarkan plat dan kode unik."""
        self.start_payment()
        self.data_kendaraan = self.plat_kendaraan.cari_kendaraan(kode_unik=kode_unik, nomor_plat=nomor_plat)
        if self.data_kendaraan:
            print(f"Kendaraan ditemukan: {self.data_kendaraan}")
            self.validate_success()
        else:
            print(f"Kendaraan dengan plat {nomor_plat} tidak ditemukan.")
            self.validate_failed()

    def calculate_payment(self):
        """Hitung biaya parkir atau denda."""
        if self.state != 'calculating_payment':
            print("Sistem tidak berada di state 'calculating_payment'.")
            return

        durasi = self.hitung_durasi(self.data_kendaraan['timestamp'])

        if self.data_kendaraan.get('kode_unik_valid', False):  # Jika kode unik valid
            self.biaya = self.plat_kendaraan.parkir.hitung_biaya(
                self.data_kendaraan['jenis_kendaraan'], durasi)
            print(f"Durasi parkir: {durasi} jam. Biaya parkir: Rp{self.biaya}.")
        else:  # Jika kode unik tidak valid
            self.biaya = self.bayar_denda(self.data_kendaraan['jenis_kendaraan'])
            print(f"Denda parkir untuk {self.data_kendaraan['jenis_kendaraan']}: Rp{self.biaya}.")

        self.calculate()

    def process_payment(self):
        """Proses pembayaran dari pengguna."""
        if self.state != 'processing_payment':
            print("Sistem tidak berada di state 'processing_payment'.")
            return

        while True:
            try:
                uang_dibayar = int(input("Masukkan nominal uang: "))
                if uang_dibayar < self.biaya:
                    print("Uang yang dibayar kurang. Silakan coba lagi.")
                else:
                    kembalian = uang_dibayar - self.biaya
                    print(f"Pembayaran berhasil. Kembalian: Rp{kembalian}.")
                    self.process_success()
                    break
            except ValueError:
                print("Input tidak valid. Masukkan angka.")

    def bayar_denda(self, jenis_kendaraan):
        """Menghitung denda parkir untuk kendaraan tertentu."""
        denda = {
            'motor': 20000,
            'mobil': 30000,
            'box': 50000,
            'truk': 100000,
            'bus': 300000
        }
        return denda.get(jenis_kendaraan, 0)

    def hitung_durasi(self, timestamp):
        """Hitung durasi parkir berdasarkan timestamp masuk (dalam hari)."""
        if isinstance(timestamp, str):
            # Parsing jika formatnya string
            timestamp_masuk = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        elif isinstance(timestamp, datetime):
            # Jika sudah berupa objek datetime, gunakan langsung
            timestamp_masuk = timestamp
        else:
            raise ValueError("Format timestamp tidak valid. Harus berupa string atau datetime.")
        
        timestamp_keluar = datetime.now()
        durasi = (timestamp_keluar - timestamp_masuk).days
        if (timestamp_keluar - timestamp_masuk).seconds > 0:
            durasi += 1
        return durasi

    def hitung_biaya_kendaraan(self, jenis_kendaraan, durasi):
        """Menghitung biaya parkir untuk kendaraan tertentu berdasarkan hari parkir."""
        biaya = self.plat_kendaraan.parkir.hitung_biaya(jenis_kendaraan, durasi)
        return biaya