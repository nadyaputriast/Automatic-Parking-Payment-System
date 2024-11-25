from datetime import datetime
from ketersediaan_parkir import KetersediaanParkir
import uuid

class PlatKendaraan:
    def __init__(self, db):
        self.parkir = KetersediaanParkir()
        self.data_kendaraan = []
        self.db = db

    def buat_kode_unik(self, nomor_plat):
        unique_id = str(uuid.uuid4())[:8]
        kode_unik = f"{nomor_plat}-{unique_id}"
        return kode_unik

    def catat_kendaraan(self, jenis_kendaraan, nomor_plat, allocated_slot=None, id_admin=None):
        slot = allocated_slot if allocated_slot else self.parkir.alokasikan_slot(jenis_kendaraan)
        
        if slot:
            kode_unik = self.buat_kode_unik(nomor_plat)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for kendaraan in self.data_kendaraan:
                if kendaraan['nomor_plat'] == nomor_plat:
                    print(f"Error: Kendaraan dengan plat {nomor_plat} sudah terdaftar!")
                    return None
            
            self.data_kendaraan.append({
                'kode_unik': kode_unik,
                'nomor_plat': nomor_plat,
                'jenis_kendaraan': jenis_kendaraan,
                'slot': slot,
                'timestamp': timestamp,
                'harga': self.parkir.harga[jenis_kendaraan]
            })
            print(f"Kendaraan dengan plat {nomor_plat} dicatat pada slot {slot} pada {timestamp}.")
            
            # Simpan data ke database
            self.db.simpan_data_parkir(nomor_plat, jenis_kendaraan, timestamp, slot, id_admin)
            
            return kode_unik
        else:
            print(f"Tidak ada slot tersedia untuk {jenis_kendaraan}.")
            return None

    def hitung_durasi(self, timestamp):
        """Hitung durasi parkir dalam hari."""
        if isinstance(timestamp, str):
            waktu_masuk = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        else:
            waktu_masuk = timestamp
        waktu_keluar = datetime.now()
        durasi = (waktu_keluar - waktu_masuk).days + 1
        return durasi

    def hitung_biaya_kendaraan(self, nomor_plat):
        """Hitung biaya parkir untuk kendaraan tertentu."""
        for data in self.data_kendaraan:
            if data['nomor_plat'] == nomor_plat:
                durasi = self.hitung_durasi(data['timestamp'])
                biaya = self.parkir.hitung_biaya(data['jenis_kendaraan'], durasi)
                print(f"Kendaraan dengan plat {nomor_plat}: \nDurasi {durasi} hari. \nBiaya Rp{biaya}.")
                return biaya
        print(f"Tidak ditemukan data untuk plat {nomor_plat}.")
        return 0

    def tampilkan_data_kendaraan(self):
        for data in self.data_kendaraan:
            print(data)

    def kosongkan_slot(self, nomor_plat):
        for data in self.data_kendaraan:
            if data['nomor_plat'] == nomor_plat:
                self.parkir.kosongkan_slot(data['jenis_kendaraan'], data['slot'])
                waktu_keluar = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                pembayaran = self.hitung_biaya_kendaraan(nomor_plat)
                self.db.update_waktu_keluar(nomor_plat, waktu_keluar, pembayaran)
                self.data_kendaraan.remove(data)  # Hapus data kendaraan dari daftar
                print(f"Slot {data['slot']} untuk kendaraan dengan plat {data['nomor_plat']} telah dikosongkan.")
                return
        print("Nomor plat tidak ditemukan.")

    def cari_kendaraan(self, kode_unik=None, nomor_plat=None):
        """Cari kendaraan berdasarkan kode unik atau nomor plat."""
        for kendaraan in self.data_kendaraan:
            if kode_unik and kendaraan['kode_unik'] == kode_unik:
                return kendaraan
            if nomor_plat and kendaraan['nomor_plat'] == nomor_plat:
                return kendaraan
        return None

# Contoh penggunaan
if __name__ == "__main__":
    from database import Database
    db = Database()
    plat_kendaraan = PlatKendaraan(db)
    plat_kendaraan.catat_kendaraan('motor', 'B1234XYZ')
    plat_kendaraan.tampilkan_data_kendaraan()
    plat_kendaraan.kosongkan_slot('B1234XYZ')
    plat_kendaraan.tampilkan_data_kendaraan()