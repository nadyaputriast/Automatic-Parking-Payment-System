import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host="localhost", user="root", password="", database="parkir"):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            if query.strip().lower().startswith("select"):
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.connection.rollback()
            return False

    def verify_login(self, username, password):
        """
        Memverifikasi apakah username dan password cocok
        """
        try:
            # Gunakan parameterized query untuk mencegah SQL injection
            query = "SELECT * FROM admin WHERE username = %s AND password = %s"
            self.cursor.execute(query, (username, password))
            result = self.cursor.fetchone()
            
            # Jika ditemukan hasil, berarti login sukses
            return result if result else None
            
        except Error as e:
            print(f"Error during login verification: {str(e)}")
            return None

    def is_kendaraan_parkir(self, nomor_plat):
        """
        Mengecek apakah kendaraan sedang parkir
        """
        query = "SELECT COUNT(*) as total FROM parkir WHERE plat = %s AND waktu_keluar IS NULL"
        result = self.execute_query(query, (nomor_plat,))
        return result[0]['total'] > 0

    def simpan_data_parkir(self, nomor_plat, jenis_kendaraan, timestamp, slot, id_admin):
        """
        Menyimpan data parkir dengan pengecekan ketat
        """
        try:
            # Cek apakah kendaraan sedang parkir
            if self.is_kendaraan_parkir(nomor_plat):
                print(f"Kendaraan dengan plat {nomor_plat} masih dalam status parkir!")
                return False
            
            # Jika aman, simpan data baru
            query = """
                INSERT INTO parkir (plat, jenis_kendaraan, waktu_masuk, slot, id_admin)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.execute_query(query, (nomor_plat, jenis_kendaraan, timestamp, slot, id_admin))
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False

    def update_waktu_keluar(self, plat, waktu_keluar, pembayaran):
        query = """
        UPDATE parkir
        SET waktu_keluar = %s, pembayaran = %s
        WHERE plat = %s AND waktu_keluar IS NULL
        """
        return self.execute_query(query, (waktu_keluar, pembayaran, plat))

    def cari_kendaraan(self, plat=None, kode_unik=None, id_admin=None):
        if plat:
            query = "SELECT * FROM parkir WHERE plat = %s AND waktu_keluar IS NULL AND id_admin = %s"
            params = (plat, id_admin)
        elif kode_unik:
            query = "SELECT * FROM parkir WHERE id = %s AND waktu_keluar IS NULL AND id_admin = %s"
            params = (kode_unik, id_admin)
        else:
            return None
        
        result = self.execute_query(query, params)
        return result[0] if result else None

    def ambil_data_parkir(self, id_admin):
        query = "SELECT * FROM parkir WHERE id_admin = %s AND waktu_keluar IS NULL"
        result = self.execute_query(query, (id_admin,))
        return result if result else []
    
    def ambil_ketersediaan_slot(self, id_admin):
        query = """
        SELECT jenis_kendaraan, COUNT(*) as terisi
        FROM parkir
        WHERE id_admin = %s AND waktu_keluar IS NULL
        GROUP BY jenis_kendaraan
        """
        return self.execute_query(query, (id_admin,))