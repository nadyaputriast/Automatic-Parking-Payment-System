from delta_function import delta
from ketersediaan_parkir import KetersediaanParkir
from plat_kendaraan import PlatKendaraan

def main():
    parkir = KetersediaanParkir()
    plat_kendaraan = PlatKendaraan()

    while True:
        print("\n=== Sistem Parkir ===")
        print("1. Kendaraan Masuk")
        print("2. Kendaraan Keluar")
        print("3. Tampilkan Data Kendaraan")
        print("4. Keluar Program")

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
                            current_state = 'rekam_plat_nomor' if slot_dialokasikan else 'keluar'
                        else:
                            print("Slot parkir penuh. Kendaraan diarahkan keluar.")
                            current_state = 'keluar'

                    # Rekam plat nomor
                    if current_state == 'rekam_plat_nomor':
                        nomor_plat = input("\nMasukkan plat nomor kendaraan: ").strip()
                        plat_kendaraan.catat_kendaraan(jenis_kendaraan, nomor_plat)
                        current_state = 'cetak_tiket_parkir'

                    # Cetak tiket parkir
                    if current_state == 'cetak_tiket_parkir':
                        print("Tiket parkir telah dicetak.")
                        current_state = final_state

                else:
                    print("Transisi tidak valid. Ulangi input.")

            print("Proses kendaraan masuk selesai.")

        elif opsi == '2':  # Kendaraan Keluar
            nomor_plat = input("Masukkan nomor plat kendaraan: ").strip()
            # Cari kendaraan berdasarkan plat nomor dan kosongkan slot
            for data in plat_kendaraan.data_kendaraan:
                if data['nomor_plat'] == nomor_plat:
                    parkir.kosongkan_slot(data['jenis_kendaraan'], data['slot'])
                    biaya = plat_kendaraan.hitung_biaya_kendaraan(nomor_plat)
                    print(f"\nBiaya parkir kendaraan {nomor_plat} : {biaya} rupiah")
                    break
            else:
                print(f"Kendaraan dengan plat {nomor_plat} tidak ditemukan.")

        elif opsi == '3':  # Tampilkan Data Kendaraan
            print("\n=== Data Kendaraan ===")
            plat_kendaraan.tampilkan_data_kendaraan()

        elif opsi == '4':  # Keluar Program
            print("Program selesai.")
            break

        else:
            print("Opsi tidak valid. Silakan pilih 1, 2, 3, atau 4.")

if __name__ == "__main__":
    main()