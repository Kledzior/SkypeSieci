import socket
import pyaudio
import struct

# Konfiguracja połączenia z serwerem
server_ip = '127.0.0.1'
server_port = 8888

# Tworzymy gniazdo klienta
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

# Konfiguracja audio
CHUNK = 1024*2
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Funkcja do wysyłania audio
def send_audio():
    while True:
        audio_data = stream.read(CHUNK)  # Odczyt audio z mikrofonu
        audio_message_size = struct.pack("L", len(audio_data))  # Rozmiar wiadomości w bajtach
        # Wysyłanie prefiksu + rozmiar wiadomości + dane audio
        client_socket.sendall(b"AUDIO" + audio_message_size + audio_data)

# Uruchomienie nadawania audio
try:
    while True:
        send_audio()  # Przesyłanie audio
except KeyboardInterrupt:
    print("Zakończono nadawanie audio.")

# Zwolnienie zasobów
stream.stop_stream()
stream.close()
audio.terminate()
client_socket.close()
