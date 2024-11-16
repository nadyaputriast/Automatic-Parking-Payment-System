from delta_function import delta
from ketersediaan_parkir import KetersediaanParkir
from plat_kendaraan import PlatKendaraan
from pembayaran import Pembayaran

def main():
    parkir = KetersediaanParkir()
    plat_kendaraan = PlatKendaraan()
    pembayaran = Pembayaran(plat_kendaraan)
    
    while True:
        print("\n=== Sistem Parkir ===")
        print("1. Kendaraan Masuk")
        print("2. Kendaraan Keluar")
        print("3. Keluar Program")

        opsi = input("Pilih opsi: ").strip()

        if opsi == '1':  # Kendaraan Masuk
            current_state = 'start'
            final_state = 'keluar'
            jenis_kendaraan = None
            slot_dialokasikan = None

            while current_state != final_state:
                print(f"\nCurrent State: {current_state}")

                symbol = input("Input symbol: ").strip()

                # Panggil fungsi delta untuk mendapatkan next state
                next_states = delta(current_state, symbol)

                if next_states:
                    current_state = next_states.pop()
                    print(f"Transisi ke state: {current_state}")

                    # Identifikasi jenis kendaraan berdasarkan state
                    if current_state in ['motor', 'mobil', 'box', 'truk', 'bus']:
                        jenis_kendaraan = current_state
                        print(f"Jenis kendaraan: {jenis_kendaraan}")

                    # Cek ketersediaan parkir
                    if current_state == 'cek_ketersediaan_parkir':
                        if parkir.cek_ketersediaan(jenis_kendaraan):
                            slot_dialokasikan = parkir.alokasikan_slot(jenis_kendaraan)
                            if slot_dialokasikan:
                                current_state = 'rekam_plat_nomor'
                        else:
                            print("Slot parkir penuh. Kendaraan diarahkan keluar.")
                            current_state = 'keluar'

                    # Rekam plat nomor
                    if current_state == 'rekam_plat_nomor':
                        nomor_plat = input("\nMasukkan plat nomor kendaraan: ").strip()
                        kode_unik = plat_kendaraan.catat_kendaraan(jenis_kendaraan, nomor_plat, slot_dialokasikan)
                        if kode_unik:
                            current_state = 'cetak_tiket_parkir'
                        else:
                            parkir.kosongkan_slot(jenis_kendaraan, slot_dialokasikan)
                            current_state = 'keluar'

                    # Cetak tiket parkir
                    if current_state == 'cetak_tiket_parkir':
                        if kode_unik:
                            print(f"Kode unik: {kode_unik}")
                        current_state = final_state

                else:
                    print("Transisi tidak valid. Ulangi input.")

            print("Proses kendaraan masuk selesai.")

        elif opsi == '2':  # Kendaraan Keluar
            kode_unik = input("Masukkan kode unik (ketik 'no' jika tidak ada): ").strip()
            
            # Cari kendaraan berdasarkan kode unik atau nomor plat
            kendaraan = None
            if kode_unik.lower() == "no":
                nomor_plat = input("Masukkan plat nomor kendaraan: ").strip()
                kendaraan = plat_kendaraan.cari_kendaraan(nomor_plat=nomor_plat)
            else:
                kendaraan = plat_kendaraan.cari_kendaraan(kode_unik=kode_unik)
            
            # Jika kendaraan ditemukan
            if kendaraan:
                slot = kendaraan['slot']
                jenis_kendaraan = kendaraan['jenis_kendaraan']
                nomor_plat = kendaraan['nomor_plat']
                
                print(f"Kendaraan dengan plat {nomor_plat}:")
                print(f"Jenis kendaraan: {jenis_kendaraan}")
                print(f"Slot yang digunakan: {slot}")
                
                # Proses pembayaran
                pembayaran.bayar_parkir(nomor_plat, kode_unik)
                
                # Kosongkan slot parkir
                parkir.kosongkan_slot(jenis_kendaraan, slot)
                
                # Hapus kendaraan dari data
                plat_kendaraan.data_kendaraan.remove(kendaraan)
                print("Kendaraan telah keluar. Terima kasih!")
            else:
                print("Kendaraan tidak ditemukan. Pastikan kode unik atau nomor plat benar.")

        elif opsi == '3':
            print("Program selesai.")
            break

        else:
            print("Opsi tidak valid. Silakan pilih 1, 2, atau 3.")

if __name__ == "__main__":
    main()