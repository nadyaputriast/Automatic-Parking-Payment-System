from delta_function import delta

def main():
    current_state = 'start'
    final_state = 'keluar'

    while current_state != final_state:
        print(f"Current State: {current_state}")
        
        symbol = input("Input symbol: ")
        
        next_states = delta(current_state, symbol)
        
        if next_states:
            current_state = next_states.pop()
        else:
            print("Transisi tidak valid. Ulangi input.")
    
    print("Proses selesai, final state tercapai.")
    
if __name__ == "__main__":
    main()