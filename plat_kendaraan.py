from datetime import datetime
from ketersediaan_parkir import KetersediaanParkir

class PlatKendaraan:
    def __init__(self):
        self.parkir = KetersediaanParkir()
        self.data_kendaraan = []
    
    def catat_kendaraan(self, jenis_kendaraan, nomor_plat):
        slot = self.parkir.alokasikan_slot(jenis_kendaraan)
        if slot:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.data_kendaraan.append({
                'nomor_plat': nomor_plat,
                'jenis_kendaraan': jenis_kendaraan,
                'slot': slot,
                'timestamp': timestamp,
                'harga': self.parkir.harga[jenis_kendaraan]
            })
            print(f"Kendaraan dengan plat {nomor_plat} dicatat pada slot {slot} pada {timestamp}.")
        else:
            print(f"Tidak ada slot tersedia untuk {jenis_kendaraan}.")
            return None
    
    def hitung_durasi(self, timestamp):
        """Hitung durasi parkir berdasarkan timestamp masuk."""
        timestamp_masuk = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        timestamp_keluar = datetime.now()
        durasi = (timestamp_keluar - timestamp_masuk).days + 1
        return durasi
    
    def hitung_biaya_kendaraan(self, nomor_plat):
        for data in self.data_kendaraan:
            if data['nomor_plat'] == nomor_plat:
                durasi = self.hitung_durasi(data['timestamp'])
                biaya = self.parkir.hitung_biaya(data['jenis_kendaraan'], durasi)
            print(f"Kendaraan dengan plat {nomor_plat}: \nDurasi {durasi} hari. \nBiaya Rp{biaya}.")
            return biaya
        print(f"Tidak ditemukan data untuk plat {nomor_plat}.")
        return 0
    
# Contoh penggunaan
if __name__ == "__main__":
    plat_kendaraan = PlatKendaraan()
    plat_kendaraan.catat_kendaraan('motor', 'B1234XYZ')