def delta(state, symbol):
    transitions = {
        'start': {
            '3' : {'motor'},
            '4' : {'mobil'},
            '5' : {'box'},
            '6' : {'truk'},
            '7' : {'bus'},
        },
        
        'motor' : {'1' : {'cek_ketersediaan_parkir'}},
        'mobil' : {'1' : {'cek_ketersediaan_parkir'}},
        'box' : {'1' : {'cek_ketersediaan_parkir'}},
        'truk' : {'1' : {'cek_ketersediaan_parkir'}},
        'bus' : {'1' : {'cek_ketersediaan_parkir'}},
        
        'cek_ketersediaan_parkir' : {
            '0' : {'keluar'},
            '1' : {'rekam_plat_nomor'},
        },
        
        'rekam_plat_nomor' : {'1' : {'cetak_tiket_parkir'}},
        
        'cetak_tiket_parkir' : {'2' : {'minta_tiket_parkir'}},
        
        'minta_tiket_parkir' : {
            '0' : {'bayar_denda'},
            '1' : {'bayar_parkir'},
        },
        
        'bayar_denda' : {
            '0' : {'bayar_denda'},
            '1' : {'keluar'},
        },
        
        'bayar_parkir' : {
            '0' : {'bayar_parkir'},
            '1' : {'keluar'},
        },
    }
            
    if state in transitions and symbol in transitions[state]:
        return transitions[state][symbol]
    else:
        return set()
    
    # return transitions.get(state, {}).get(symbol, [])