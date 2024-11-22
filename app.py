import streamlit as st
from datetime import datetime
from ketersediaan_parkir import KetersediaanParkir
from plat_kendaraan import PlatKendaraan
from pembayaran import Pembayaran
from database import Database

def main():
    st.title("Sistem Pembayaran Parkir Otomatis")

    db = Database()
    
    # Inisialisasi session state jika belum ada
    if 'parkir' not in st.session_state:
        st.session_state.parkir = KetersediaanParkir()
    if 'plat_kendaraan' not in st.session_state:
        st.session_state.plat_kendaraan = PlatKendaraan(db)
    if 'pembayaran' not in st.session_state:
        st.session_state.pembayaran = Pembayaran(st.session_state.plat_kendaraan)

    # Sidebar untuk navigasi
    menu = st.sidebar.selectbox("Pilih Menu", ["Kendaraan Masuk", "Kendaraan Keluar", "Data Parkir"])

    if menu == "Kendaraan Masuk":
        st.header("Kendaraan Masuk")
    
        # Pilih jenis kendaraan
        jenis_kendaraan = st.selectbox("Pilih Jenis Kendaraan:", ['motor', 'mobil', 'box', 'truk', 'bus'])
        
        if jenis_kendaraan:
            nomor_plat = st.text_input("Masukkan plat nomor kendaraan:")
            
            if nomor_plat:
                # Cek apakah kendaraan sudah terparkir
                existing_query = "SELECT * FROM parkir WHERE plat = %s AND waktu_keluar IS NULL"
                existing_kendaraan = db.execute_query(existing_query, (nomor_plat,))
                
                if existing_kendaraan:
                    st.warning("Kendaraan ini sudah terparkir.")
                else:
                    # Cek ketersediaan slot
                    if st.session_state.parkir.cek_ketersediaan(jenis_kendaraan):
                        slot_dialokasikan = st.session_state.parkir.alokasikan_slot(jenis_kendaraan)
                        if slot_dialokasikan:
                            waktu_masuk = datetime.now()
                            # Masukkan data ke database
                            insert_query = """
                                INSERT INTO parkir (plat, jenis_kendaraan, waktu_masuk, slot)
                                VALUES (%s, %s, %s, %s)
                            """
                            db.execute_query(insert_query, (nomor_plat, jenis_kendaraan, waktu_masuk, slot_dialokasikan))
                            
                            # Generate kode unik
                            kode_unik = st.session_state.plat_kendaraan.catat_kendaraan(
                                jenis_kendaraan, nomor_plat, slot_dialokasikan
                            )
                            
                            if kode_unik:
                                st.success("Tiket parkir berhasil dicatat.")
                                st.info(f"""
                                Detail Parkir:
                                - Kode Unik: {kode_unik}
                                - Plat Nomor: {nomor_plat}
                                - Jenis Kendaraan: {jenis_kendaraan}
                                - Slot Parkir: {slot_dialokasikan}
                                - Waktu Masuk: {waktu_masuk.strftime('%Y-%m-%d %H:%M:%S')}
                                - Harga tiket: Rp{st.session_state.parkir.harga[jenis_kendaraan]:}/hari
                                """)
                    else:
                        st.warning(f"Tidak ada slot parkir tersedia untuk {jenis_kendaraan}.")

    elif menu == "Kendaraan Keluar":
        st.header("Kendaraan Keluar")

        search_method = st.radio("Pilih metode pencarian:", ["Kode Unik", "Nomor Plat"])

        kendaraan = None  # Untuk menyimpan data kendaraan yang ditemukan
        is_using_kode_unik = False  # Menentukan apakah pencarian pakai kode unik

        # Pencarian kendaraan berdasarkan nomor plat atau kode unik
        if search_method == "Kode Unik":
            kode_unik = st.text_input("Masukkan kode unik:", key="kode_unik")
            kendaraan = st.session_state.plat_kendaraan.cari_kendaraan(kode_unik=kode_unik)
            if kode_unik:
                kendaraan = st.session_state.plat_kendaraan.cari_kendaraan(kode_unik=kode_unik)
                is_using_kode_unik = True
        else:
            nomor_plat = st.text_input("Masukkan nomor plat kendaraan:", key="nomor_plat")
            kendaraan = st.session_state.plat_kendaraan.cari_kendaraan(nomor_plat=nomor_plat)
            if nomor_plat:
                kendaraan = st.session_state.plat_kendaraan.cari_kendaraan(nomor_plat=nomor_plat)
                is_using_kode_unik = False

        # Menampilkan hasil pencarian jika kendaraan ditemukan
        if kendaraan:
            st.write("Detail Kendaraan:")
            st.write(f"Nomor Plat: {kendaraan['nomor_plat']}")
            st.write(f"Jenis Kendaraan: {kendaraan['jenis_kendaraan']}")
            st.write(f"Slot Parkir: {kendaraan['slot']}")
            st.write(f"Waktu Masuk: {kendaraan['timestamp']}")

            waktu_keluar = datetime.now()

            data_kendaraan = {
                'jenis_kendaraan': kendaraan['jenis_kendaraan'],
                'timestamp': kendaraan['timestamp'],
                'nomor_plat': kendaraan['nomor_plat']
            }
            
            if is_using_kode_unik:
                durasi = st.session_state.pembayaran.hitung_durasi(data_kendaraan['timestamp'])
                biaya = st.session_state.pembayaran.hitung_biaya_kendaraan(data_kendaraan)
                st.info(f"Durasi Parkir: {durasi} hari")
                st.info(f"Biaya Parkir: Rp{biaya}")
            else:
                durasi = st.session_state.pembayaran.hitung_durasi(data_kendaraan['timestamp'])
                denda = st.session_state.pembayaran.bayar_denda(data_kendaraan)
                st.info(f"Denda Parkir: Rp{denda}")
                
            pembayaran = st.number_input("Jumlah Pembayaran:", min_value=0, step=1000)
            if st.button("Proses Pembayaran"):
                if pembayaran < (biaya if is_using_kode_unik else denda):
                    st.error("Pembayaran kurang!")
                else:
                    kembalian = pembayaran - (biaya if is_using_kode_unik else denda)
                    st.success(f"Pembayaran berhasil. Kembalian: Rp{kembalian}")

                    # Update 
                    db.execute_query("""
                        UPDATE parkir
                        SET waktu_keluar = %s, pembayaran = %s
                        WHERE plat = %s AND waktu_keluar IS NULL
                    """, (waktu_keluar, biaya, kendaraan['nomor_plat']))

                    st.success("Data kendaraan berhasil diperbarui.")
                    
                    # Kosongkan slot
                    st.session_state.parkir.kosongkan_slot(kendaraan['jenis_kendaraan'], kendaraan['slot'])

                    # Hapus data kendaraan dari session_state
                    if kendaraan in st.session_state.plat_kendaraan.data_kendaraan:
                        st.session_state.plat_kendaraan.data_kendaraan.remove(kendaraan)
                    st.success("Pembayaran berhasil. Kendaraan telah keluar.")
                    
        elif (search_method == "Kode Unik" and kode_unik) or (search_method == "Nomor Plat" and nomor_plat):
            st.error("Kendaraan tidak ditemukan. Pastikan input benar.")

    elif menu == "Data Parkir":
        st.header("Data Parkir")
        
        # Tampilkan ketersediaan slot
        st.subheader("Ketersediaan Slot Parkir")
        cols = st.columns(5)
        
        for idx, jenis in enumerate(['motor', 'mobil', 'box', 'truk', 'bus']):
            with cols[idx]:
                total = len(st.session_state.parkir.slots[jenis]) + len(st.session_state.parkir.terisi[jenis])
                tersedia = total - len(st.session_state.parkir.terisi[jenis])
                st.metric(
                    jenis.capitalize(), 
                    f"{tersedia}/{total}",
                    f"Rp{st.session_state.parkir.harga[jenis]:}/hari"
                )

        # Tampilkan info denda
        st.subheader("Informasi Denda (Hilang Karcis)")
        denda_info = {
            'motor': 20000,
            'mobil': 30000,
            'box': 50000,
            'truk': 100000,
            'bus': 300000
        }
        
        denda_cols = st.columns(5)
        for idx, (jenis, nominal) in enumerate(denda_info.items()):
            with denda_cols[idx]:
                st.markdown(f"<h3>{jenis.capitalize()}</h3><h4>Rp{nominal:}</h4>", unsafe_allow_html=True)
        
        # Tampilkan data kendaraan yang sedang parkir
        st.subheader("Kendaraan Yang Sedang Parkir")
        if st.session_state.plat_kendaraan.data_kendaraan:
            data_table = []
            for kendaraan in st.session_state.plat_kendaraan.data_kendaraan:
                durasi = st.session_state.pembayaran.hitung_durasi(kendaraan['timestamp'])
                biaya = st.session_state.plat_kendaraan.parkir.hitung_biaya(
                    kendaraan['jenis_kendaraan'],
                    durasi
                )
                
                data_table.append({
                    "index": kendaraan['kode_unik'],
                    "Plat Nomor": kendaraan['nomor_plat'],
                    "Jenis": kendaraan['jenis_kendaraan'],
                    "Slot": kendaraan['slot'],
                    "Waktu Masuk": kendaraan['timestamp'],
                    "Durasi (hari)": durasi,
                    "Biaya Normal": f"Rp{biaya:}"
                })
            
            st.table(data_table)
        else:
            st.info("Tidak ada kendaraan yang sedang parkir")

if __name__ == "__main__":
    main()