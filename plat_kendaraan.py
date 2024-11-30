from datetime import datetime
from ketersediaan_parkir import KetersediaanParkir
import random
import uuid
import hashlib

class PlatKendaraan:
    states = ['idle', 'validating', 'parked', 'left', 'error']

    def __init__(self, db=None):
        self.parkir = KetersediaanParkir()
        self.data_kendaraan = []
        self.db = db
        self.state = 'idle'

        # Define state transitions
        self.transitions = {
            'idle': {'catat_kendaraan': 'validating'},
            'validating': {
                'validasi_berhasil': 'parked', 
                'validasi_gagal': 'error'
            },
            'parked': {'kosongkan_slot': 'left'},
            'left': {},
            'error': {'reset': 'idle'}
        }

    def change_state(self, action):
        """Change state based on the given action."""
        try:
            if action in self.transitions[self.state]:
                self.state = self.transitions[self.state][action]
                print(f"State changed to: {self.state}")
            else:
                raise ValueError(f"Invalid transition from state '{self.state}' with action '{action}'.")
        except Exception as e:
            print(f"State change error: {e}")
            self.state = 'error'

    def catat_kendaraan(self, jenis_kendaraan, nomor_plat, allocated_slot=None):
        """Record a vehicle in the parking system."""
        print("Starting vehicle registration...")
        
        # Input validation
        if not jenis_kendaraan or not nomor_plat:
            print("Invalid vehicle type or plate number.")
            self.change_state('validasi_gagal')
            return None

        self.change_state('catat_kendaraan')

        # Allocate parking slot
        slot = allocated_slot if allocated_slot else self.parkir.alokasikan_slot(jenis_kendaraan)
        
        if not slot:
            print(f"No available slot for {jenis_kendaraan}.")
            self.change_state('validasi_gagal')
            return None

        # Check if vehicle is already registered
        if self.cari_kendaraan(nomor_plat):
            print(f"Vehicle with plate {nomor_plat} is already registered!")
            return None

        # Generate unique code
        kode_unik = self.buat_kode_unik(nomor_plat)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Record vehicle
        kendaraan_tercatat = {
            'kode_unik': kode_unik,
            'jenis_kendaraan': jenis_kendaraan,
            'nomor_plat': nomor_plat,
            'slot': slot,
            'timestamp': timestamp
        }
        
        self.data_kendaraan.append(kendaraan_tercatat)
        self.change_state('validasi_berhasil')
        
        # Optional: Save to database
        if self.db:
            try:
                self.db.save_vehicle(kendaraan_tercatat)
            except Exception as e:
                print(f"Database save error: {e}")

        print(f"Vehicle {nomor_plat} successfully registered.")
        return kode_unik

    def cari_kendaraan(self, nomor_plat=None, kode_unik=None):
        """Search for a vehicle by plate number or unique code."""
        if kode_unik:
            return next((kendaraan for kendaraan in self.data_kendaraan if kendaraan['kode_unik'] == kode_unik), None)
        if nomor_plat:
            return next((kendaraan for kendaraan in self.data_kendaraan if kendaraan['nomor_plat'] == nomor_plat), None)
        return None

    def buat_kode_unik(self, nomor_plat):
        unique_id = str(uuid.uuid4())[:8]
        kode_unik = f"{nomor_plat}-{unique_id}"
        return kode_unik