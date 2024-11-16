from datetime import datetime
from ketersediaan_parkir import KetersediaanParkir
import uuid

class PlatKendaraan:
    def __init__(self):
        self.parkir = KetersediaanParkir()
        self.data_kendaraan = []
    
    def buat_kode_unik(self, nomor_plat):
        unique_id = str(uuid.uuid4())[:8]
        kode_unik = f"{nomor_plat}-{unique_id}"
        return kode_unik
    
    def catat_kendaraan(self, jenis_kendaraan, nomor_plat, allocated_slot=None):
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
            return kode_unik
        else:
            print(f"Tidak ada slot tersedia untuk {jenis_kendaraan}.")
            return None
    
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
    plat_kendaraan = PlatKendaraan()
    plat_kendaraan.catat_kendaraan('motor', 'B1234XYZ')