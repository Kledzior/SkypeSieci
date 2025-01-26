import cv2
import socket
import pickle
import struct
import pyaudio
import time

# Konfiguracja połączenia z serwerem
server_ip = '127.0.0.1'
server_port = 8888

# Tworzymy gniazdo klienta
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

# Konfiguracja kamery
cap = cv2.VideoCapture(0)

# Konfiguracja audio
CHUNK = 1024/4
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Funkcja do wysyłania obrazu
def send_video():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Błąd: Nie udało się przechwycić obrazu")
            break

        # Serializacja ramki obrazu
        try:
            data = pickle.dumps(frame)
            message_size = struct.pack("L", len(data))  # Rozmiar wiadomości w bajtach

            # Wysyłanie prefiksu + rozmiar wiadomości + dane
            client_socket.sendall(b"VIDEO" + message_size + data)
            print("Wysłano obraz...")
            time.sleep(0.1)  # Dodanie opóźnienia między wysyłkami
        except Exception as e:
            print(f"Błąd w przesyłaniu obrazu: {e}")
            break

# Funkcja do wysyłania audio
def send_audio():
    while True:
        audio_data = stream.read(CHUNK)
        audio_message_size = struct.pack("L", len(audio_data))
        client_socket.sendall(b"AUDIO" + audio_message_size + audio_data)

# Uruchomienie wątków
import threading
video_thread = threading.Thread(target=send_video)
audio_thread = threading.Thread(target=send_audio)

video_thread.daemon = True
audio_thread.daemon = True
video_thread.start()
audio_thread.start()

# Główna pętla nadawcy
try:
    while True:
        time.sleep(1)  # Wykonuje jakiekolwiek inne operacje lub czeka
except KeyboardInterrupt:
    print("Zakończono nadawcę")

cap.release()
stream.stop_stream()
stream.close()
audio.terminate()
client_socket.close()
