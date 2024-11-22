from plat_kendaraan import PlatKendaraan
from datetime import datetime

class Pembayaran:
    def __init__(self, plat_kendaraan):
        self.plat_kendaraan = plat_kendaraan
    
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
    
    def hitung_biaya_kendaraan(self, data_kendaraan):
        """Menghitung biaya parkir untuk kendaraan tertentu berdasarkan hari parkir."""
        if not isinstance(data_kendaraan, dict):
            raise ValueError("Data kendaraan harus berupa dictionary.")
        
        if 'timestamp' not in data_kendaraan or 'jenis_kendaraan' not in data_kendaraan:
            raise KeyError("Data kendaraan harus memiliki 'timestamp' dan 'jenis_kendaraan'")
        
        durasi = self.hitung_durasi(data_kendaraan['timestamp'])
        biaya = self.plat_kendaraan.parkir.hitung_biaya(data_kendaraan['jenis_kendaraan'], durasi)
        return biaya
    
    def bayar_parkir(self, nomor_plat, kode_unik=None):
        """Memproses pembayaran berdasarkan kode unik dan nomor plat."""
        data_kendaraan = self.plat_kendaraan.cari_kendaraan(kode_unik=kode_unik, nomor_plat=nomor_plat)
        
        if not data_kendaraan:
            print(f"Kendaraan dengan plat {nomor_plat} tidak ditemukan.")
            return None
        
        if kode_unik and data_kendaraan['kode_unik'] == kode_unik:
            # Validasi kode unik dan hitung biaya
            biaya = self.hitung_biaya_kendaraan(data_kendaraan['jenis_kendaraan'], self.hitung_durasi(data_kendaraan['timestamp']))
            if biaya > 0:
                print(f"Biaya parkir: Rp{biaya}")
                print("Silakan lakukan pembayaran.")
                
                uang_dibayar = int(input("Masukkan nominal uang: "))
                
                if uang_dibayar < biaya:
                    print("Uang yang dibayar kurang.")
                    return self.bayar_parkir(nomor_plat, kode_unik)
                elif uang_dibayar > biaya:
                    kembalian = uang_dibayar - biaya
                    print(f"Kembalian: Rp{kembalian}")
                else:
                    print("Pembayaran berhasil.")
                    return data_kendaraan
        else:
            # Jika kode unik tidak valid, bayar denda
            print("Kode unik tidak valid atau tidak tersedia.")
            return self.bayar_denda(data_kendaraan)
    
    def bayar_denda(self, data_kendaraan):
        """Memproses pembayaran denda jika kode unik tidak tersedia."""
        jenis_kendaraan = data_kendaraan['jenis_kendaraan']
        denda = {
            'motor': 20000,
            'mobil': 30000,
            'box': 50000,
            'truk': 100000,
            'bus': 300000
        }
        return denda.get(jenis_kendaraan, 0)
        
        if jenis_kendaraan in denda:
            print(f"Denda untuk {jenis_kendaraan}: Rp{denda[jenis_kendaraan]}")
            print("Silakan lakukan pembayaran denda.")
            
            uang_dibayar = int(input("Masukkan nominal uang: "))
            
            if uang_dibayar < denda[jenis_kendaraan]:
                print("Uang yang dibayar kurang.")
                return self.bayar_denda(data_kendaraan)
            elif uang_dibayar > denda[jenis_kendaraan]:
                kembalian = uang_dibayar - denda[jenis_kendaraan]
                print(f"Kembalian: Rp{kembalian}")
            else:
                print("Pembayaran denda berhasil.")
                data_kendaraan
        else:
            print("Jenis kendaraan tidak valid.")
            return None


if __name__ == "__main__":
    plat_kendaraan = PlatKendaraan()
    pembayaran = Pembayaran(plat_kendaraan)
    
    nomor_plat = input("Masukkan nomor plat kendaraan: ").strip()
    kode_unik = input("Masukkan kode unik kendaraan (ketik 'no' jika tidak ada): ").strip()
    
    if kode_unik.lower() == "no":
        kode_unik = None
    
    pembayaran.bayar_parkir(nomor_plat, kode_unik)