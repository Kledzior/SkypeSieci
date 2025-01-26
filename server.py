import socket
import cv2
import pickle
import struct
import pyaudio
import threading

# Konfiguracja serwera
server_ip = '127.0.0.1'
server_port = 8888

# Tworzymy gniazdo serwera
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(2)  # Nasłuchujemy na dwa połączenia (sender + receiver)

print(f"Serwer nasłuchuje na {server_ip}:{server_port}...")
sender_socket, sender_address = server_socket.accept()
print(f"Połączono z nadawcą {sender_address}")

receiver_socket, receiver_address = server_socket.accept()
print(f"Połączono z odbiorcą {receiver_address}")

# Konfiguracja audio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
audio = pyaudio.PyAudio()

# Funkcja do przesyłania audio i wideo z nadawcy do odbiorcy
def forward_data():
    try:
        while True:
            # Odbieranie prefiksu (AUDIO/VIDEO) od nadawcy
            prefix = sender_socket.recv(5)
            if not prefix:
                break

            # Odbieranie rozmiaru wiadomości
            message_size = sender_socket.recv(4)
            if not message_size:
                break
            data_size = struct.unpack("L", message_size)[0]

            # Odbieranie danych
            data = b""
            while len(data) < data_size:
                packet = sender_socket.recv(data_size - len(data))
                data += packet

            # Wysyłanie danych do odbiorcy
            receiver_socket.sendall(prefix + message_size + data)

    except Exception as e:
        print(f"Błąd w przesyłaniu danych: {e}")

# Uruchomienie wątku do przesyłania danych
thread = threading.Thread(target=forward_data)
thread.daemon = True
thread.start()

# Główna pętla serwera
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Zakończono serwer")

# Zwolnienie zasobów
sender_socket.close()
receiver_socket.close()
server_socket.close()
audio.terminate()
