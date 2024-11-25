import streamlit as st
from datetime import datetime
from ketersediaan_parkir import KetersediaanParkir
from plat_kendaraan import PlatKendaraan
from pembayaran import Pembayaran
from database import Database

def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'id_admin' not in st.session_state:
        st.session_state.id_admin = None

def login(db):
    st.title("Login Admin")
    
    initialize_session_state()
    
    with st.form("login_form"):
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:  # Check if fields are not empty
                # Verify login
                result = db.verify_login(username, password)
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.id_admin = result['id_admin']
                    st.session_state.login_attempts = 0
                    st.success("Login berhasil!")
                    st.rerun()  # Refresh halaman
                else:
                    st.session_state.login_attempts += 1
                    st.error(f"Username atau password salah! Percobaan ke-{st.session_state.login_attempts}")
            else:
                st.error("Username dan password tidak boleh kosong!")

def main():
    st.title("Sistem Pembayaran Parkir Otomatis")

    db = Database()

    # Check login status
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login(db)
        return

    if 'parkir' not in st.session_state:
        st.session_state.parkir = KetersediaanParkir()
    if 'plat_kendaraan' not in st.session_state:
        st.session_state.plat_kendaraan = PlatKendaraan(db)
    if 'pembayaran' not in st.session_state:
        st.session_state.pembayaran = Pembayaran(st.session_state.plat_kendaraan)

    # Sidebar untuk navigasi
    menu = st.sidebar.selectbox("Pilih Menu", ["Kendaraan Masuk", "Kendaraan Keluar", "Data Parkir", "Log Out"])

    if menu == "Log Out":
        st.session_state.logged_in = False
        del st.session_state.username
        del st.session_state.id_admin
        st.success("Anda telah logout.")
        st.rerun()  # Refresh halaman dan kembali ke form login

    if menu == "Kendaraan Masuk":
        st.header("Kendaraan Masuk")
    
        # Pilih jenis kendaraan
        jenis_kendaraan = st.selectbox("Pilih Jenis Kendaraan:", ['motor', 'mobil', 'box', 'truk', 'bus'])
        
        if jenis_kendaraan:
            nomor_plat = st.text_input("Masukkan plat nomor kendaraan:")
            
            if nomor_plat:
                # Cek apakah kendaraan sudah terparkir
                existing_query = "SELECT * FROM parkir WHERE plat = %s AND waktu_keluar IS NULL AND id_admin = %s"
                existing_kendaraan = db.execute_query(existing_query, (nomor_plat, st.session_state.id_admin))
                
                if existing_kendaraan:
                    st.warning("Kendaraan ini sudah terparkir.")
                else:
                    # Cek ketersediaan slot
                    if st.session_state.parkir.cek_ketersediaan(jenis_kendaraan):
                        slot_dialokasikan = st.session_state.parkir.alokasikan_slot(jenis_kendaraan)
                        if slot_dialokasikan:
                            waktu_masuk = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            # Masukkan data ke database
                            insert_query = """
                                INSERT INTO parkir (plat, jenis_kendaraan, waktu_masuk, slot, id_admin)
                                VALUES (%s, %s, %s, %s, %s)
                            """
                            id_admin = st.session_state.id_admin
                            if db.execute_query(insert_query, (nomor_plat, jenis_kendaraan, waktu_masuk, slot_dialokasikan, id_admin)):
                                st.success("Data kendaraan berhasil ditambahkan ke database.")
                                
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
                                    - Waktu Masuk: {waktu_masuk}
                                    """)
                            else:
                                st.error("Gagal menambahkan data kendaraan ke database.")
                        else:
                            st.warning(f"Tidak ada slot parkir tersedia untuk {jenis_kendaraan}.")

    if menu == "Kendaraan Keluar":
        st.header("Kendaraan Keluar")

        search_method = st.radio("Pilih metode pencarian:", ["Kode Unik", "Nomor Plat"])

        if search_method == "Kode Unik":
            kode_unik = st.text_input("Masukkan kode unik:", key="kode_unik")
            if kode_unik:
                kendaraan = st.session_state.plat_kendaraan.cari_kendaraan(kode_unik=kode_unik, id_admin=st.session_state.id_admin)
                if kendaraan:
                    st.write("Detail Kendaraan:")
                    st.write(f"Nomor Plat: {kendaraan['nomor_plat']}")
                    st.write(f"Jenis Kendaraan: {kendaraan['jenis_kendaraan']}")
                    st.write(f"Slot Parkir: {kendaraan['slot']}")
                    st.write(f"Waktu Masuk: {kendaraan['timestamp']}")

                    waktu_keluar = datetime.now()
                    waktu_masuk = kendaraan['timestamp']
                    if isinstance(waktu_masuk, str):
                        waktu_masuk = datetime.strptime(waktu_masuk, '%Y-%m-%d %H:%M:%S')
                    durasi = st.session_state.pembayaran.hitung_durasi(waktu_masuk)
                    biaya = st.session_state.pembayaran.hitung_biaya_kendaraan(kendaraan['jenis_kendaraan'], durasi)
                    st.info(f"Durasi Parkir: {durasi} hari")
                    st.info(f"Biaya Parkir: Rp{biaya}")

                    pembayaran = st.number_input("Jumlah Pembayaran:", min_value=0, step=1000)
                    if st.button("Proses Pembayaran"):
                        if pembayaran < biaya:
                            st.error("Pembayaran kurang!")
                        else:
                            kembalian = pembayaran - biaya
                            st.success(f"Pembayaran berhasil. Kembalian: Rp{kembalian}")

                            # Update waktu keluar dan pembayaran di database
                            db.execute_query("""
                                UPDATE parkir
                                SET waktu_keluar = %s, pembayaran = %s
                                WHERE plat = %s AND waktu_keluar IS NULL AND id_admin = %s
                            """, (waktu_keluar, biaya, kendaraan['nomor_plat'], st.session_state.id_admin))

                            st.success("Data kendaraan berhasil diperbarui.")

                            # Kosongkan slot dan hapus data kendaraan dari session state
                            st.session_state.parkir.kosongkan_slot(kendaraan['jenis_kendaraan'], kendaraan['slot'])
                            if kendaraan in st.session_state.plat_kendaraan.data_kendaraan:
                                st.session_state.plat_kendaraan.data_kendaraan.remove(kendaraan)
                            st.success("Pembayaran berhasil. Kendaraan telah keluar.")
                else:
                    st.error("Kendaraan tidak ditemukan. Pastikan input benar.")

        elif search_method == "Nomor Plat":
            nomor_plat = st.text_input("Masukkan nomor plat kendaraan:", key="nomor_plat")
            if nomor_plat:
                kendaraan = st.session_state.plat_kendaraan.cari_kendaraan(nomor_plat=nomor_plat, id_admin=st.session_state.id_admin)
                if kendaraan:
                    st.write("Detail Kendaraan:")
                    st.write(f"Nomor Plat: {kendaraan['nomor_plat']}")
                    st.write(f"Jenis Kendaraan: {kendaraan['jenis_kendaraan']}")
                    st.write(f"Slot Parkir: {kendaraan['slot']}")
                    st.write(f"Waktu Masuk: {kendaraan['timestamp']}")

                    waktu_keluar = datetime.now()
                    waktu_masuk = kendaraan['timestamp']
                    if isinstance(waktu_masuk, str):
                        waktu_masuk = datetime.strptime(waktu_masuk, '%Y-%m-%d %H:%M:%S')
                    durasi = st.session_state.pembayaran.hitung_durasi(waktu_masuk)
                    denda = st.session_state.pembayaran.bayar_denda(kendaraan['jenis_kendaraan'])
                    st.info(f"Denda Parkir: Rp{denda}")

                    pembayaran = st.number_input("Jumlah Pembayaran:", min_value=0, step=1000)
                    if st.button("Proses Pembayaran"):
                        if pembayaran < denda:
                            st.error("Pembayaran kurang!")
                        else:
                            kembalian = pembayaran - denda
                            st.success(f"Pembayaran berhasil. Kembalian: Rp{kembalian}")

                            # Update waktu keluar dan pembayaran di database
                            db.execute_query("""
                                UPDATE parkir
                                SET waktu_keluar = %s, pembayaran = %s
                                WHERE plat = %s AND waktu_keluar IS NULL AND id_admin = %s
                            """, (waktu_keluar, denda, kendaraan['nomor_plat'], st.session_state.id_admin))

                            st.success("Data kendaraan berhasil diperbarui.")

                            # Kosongkan slot dan hapus data kendaraan dari session state
                            st.session_state.parkir.kosongkan_slot(kendaraan['jenis_kendaraan'], kendaraan['slot'])
                            if kendaraan in st.session_state.plat_kendaraan.data_kendaraan:
                                st.session_state.plat_kendaraan.data_kendaraan.remove(kendaraan)
                            st.success("Pembayaran berhasil. Kendaraan telah keluar.")
                else:
                    st.error("Kendaraan tidak ditemukan. Pastikan input benar.")

    if menu == "Data Parkir":
        st.header("Data Parkir")
        
        kapasitas = {
            "motor": 100,
            "mobil": 50,
            "box": 20,
            "truk": 10,
            "bus": 5
        }

        st.subheader("Ketersediaan Slot Parkir")
        cols = st.columns(len(kapasitas))

        ketersediaan_data = db.ambil_ketersediaan_slot(st.session_state.id_admin)

        for idx, (jenis, total) in enumerate(kapasitas.items()):
            with cols[idx]:
                terisi = next((item['terisi'] for item in ketersediaan_data if item['jenis_kendaraan'] == jenis), 0)
                tersedia = total - terisi
                                
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
        data_parkir = db.ambil_data_parkir(st.session_state.id_admin)
        if data_parkir:
            data_parkir_list = []
            for kendaraan in data_parkir:
                durasi = st.session_state.pembayaran.hitung_durasi(kendaraan['waktu_masuk'])
                biaya = st.session_state.plat_kendaraan.parkir.hitung_biaya(
                    kendaraan['jenis_kendaraan'],
                    durasi
                )
                data_parkir_list.append({
                    "Plat Nomor": kendaraan['plat'],
                    "Jenis": kendaraan['jenis_kendaraan'],
                    "Slot": kendaraan['slot'],
                    "Waktu Masuk": kendaraan['waktu_masuk'],
                    "Durasi (hari)": durasi,
                    "Biaya Normal": f"Rp{biaya:}"
                })
            
            st.table(data_parkir_list)
        else:
            st.info("Tidak ada kendaraan yang sedang parkir.")

if __name__ == "__main__":
    main()