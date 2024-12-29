import socket
import tkinter as tk
import re #module for regular expressions

def check_correctness(ip_addr, port):
    try:
        socket.gethostbyname(ip_addr)
        print(f"Valid IP address entered: {ip_addr}")
    except socket.gaierror:
        print("Invalid IP address format or does not exist")
        return False

    if port.isdigit() and 0 <= int(port) <= 65535:
        print(f"Valid port number entered: {port}")
    else:
        print("Invalid port number format")
        return False

    return True

def connect(root):
    ip_entry = tk.Entry(root)
    ip_entry.pack(pady=20)
    port_entry = tk.Entry(root)
    port_entry.pack(pady=30)

    def on_button_click():
        ip_addr = ip_entry.get()
        port    = port_entry.get()      

        if check_correctness(ip_addr, port):
            HOST = ip_addr
            PORT = int(port)
            try:
                with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect((HOST,PORT))

                    s.sendall("TEXTHello, world".encode())
                    data = s.recv(1024).decode()

                print(f"RECEIVED {data}")
            except socket.timeout:
                print("Connection timed out. The IP address might be incorrect.")
            except ConnectionRefusedError:
                print("Connection refused. Server might not be running or the provided port is incorrect.")
            except Exception as e:
                print(f"An error occurred: {e}")

    button = tk.Button(root, text="Connect", command=on_button_click)
    button.pack(pady=10)     

def init():
    root = tk.Tk()
    root.title("Budget Skype")
    root.geometry("600x600")
    connect(root)
    return root

def main():
    root = init()
    root.mainloop()

if __name__ == "__main__":
    main()

    