import socket
import pyaudio
import struct

# Konfiguracja połączenia z serwerem
server_ip = '127.0.0.1'
server_port = 8888

# Tworzymy gniazdo klienta
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

# Konfiguracja odtwarzania audio
CHUNK = 1024*2
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

# Funkcja do odbierania danych
def receive_all(sock, size):
    """Odbiera dokładnie `size` bajtów danych z gniazda."""
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            raise ConnectionError("Połączenie zakończone przez nadawcę")
        data += packet
    return data

# Odbieranie audio
try:
    while True:
        # Odbieranie prefiksu (AUDIO)
        prefix = receive_all(client_socket, 5)
        if prefix != b"AUDIO":
            break
        
        # Odbieranie rozmiaru wiadomości
        message_size_data = receive_all(client_socket, 4)
        message_size = struct.unpack("L", message_size_data)[0]
        
        # Odbieranie danych audio
        audio_data = receive_all(client_socket, message_size)

        # Odtwarzanie odebranego dźwięku
        stream.write(audio_data)

except Exception as e:
    print(f"Błąd: {e}")

# Zwolnienie zasobów
client_socket.close()
stream.stop_stream()
stream.close()
audio.terminate()
