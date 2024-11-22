import mysql.connector

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
            self.connection.commit()
            if query.strip().lower().startswith("select"):
                return self.cursor.fetchall()
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.connection.rollback()
            return False

    def is_kendaraan_parkir(self, nomor_plat):
        """
        Mengecek apakah kendaraan sedang parkir
        """
        self.cursor.execute(
            "SELECT COUNT(*) as total FROM parkir WHERE plat = %s AND waktu_keluar IS NULL",
            (nomor_plat,)
        )
        result = self.cursor.fetchone()
        return result['total'] > 0

    def simpan_data_parkir(self, nomor_plat, jenis_kendaraan, timestamp, slot):
        """
        Menyimpan data parkir dengan pengecekan ketat
        """
        # 1. Lock tabel untuk mencegah race condition
        self.cursor.execute("LOCK TABLES parkir WRITE")
        
        try:
            # 2. Cek apakah kendaraan sedang parkir
            if self.is_kendaraan_parkir(nomor_plat):
                print(f"Kendaraan dengan plat {nomor_plat} masih dalam status parkir!")
                return False
            
            # 3. Jika aman, simpan data baru
            query = """
                INSERT INTO parkir (plat, jenis_kendaraan, waktu_masuk, slot)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(query, (nomor_plat, jenis_kendaraan, timestamp, slot))
            self.connection.commit()
            return True
            
        except mysql.connector.Error as err:
            print(f"Error saat menyimpan: {err}")
            self.connection.rollback()
            return False
            
        finally:
            # 4. Selalu unlock tabel
            self.cursor.execute("UNLOCK TABLES")

    def update_waktu_keluar(self, plat, waktu_keluar, biaya):
        query = """
            UPDATE parkir 
            SET waktu_keluar = %s, pembayaran = %s
            WHERE plat = %s AND waktu_keluar IS NULL
        """
        return self.execute_query(query, (waktu_keluar, biaya, plat))

    def get_kendaraan_aktif(self):
        query = "SELECT * FROM parkir WHERE waktu_keluar IS NULL"
        return self.execute_query(query)

    def cari_kendaraan(self, plat=None, kode_unik=None):
        if plat:
            query = "SELECT * FROM parkir WHERE plat = %s AND waktu_keluar IS NULL"
            params = (plat,)
        elif kode_unik:
            query = "SELECT * FROM parkir WHERE id = %s AND waktu_keluar IS NULL"
            params = (kode_unik,)
        else:
            return None
        
        result = self.execute_query(query, params)
        return result[0] if result else None