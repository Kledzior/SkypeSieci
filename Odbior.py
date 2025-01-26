import socket
import cv2
import pickle
import struct
import pyaudio

# Konfiguracja połączenia z serwerem
server_ip = '127.0.0.1'
server_port = 8888

# Tworzymy gniazdo klienta
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

# Konfiguracja odtwarzania audio
CHUNK = 1024/4
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

# Odbieranie strumienia wideo i audio
try:
    while True:
        # Odbieranie prefiksu (AUDIO/VIDEO)
        prefix = receive_all(client_socket, 5)
        if not prefix:
            break

        # Odbieranie rozmiaru wiadomości
        message_size_data = receive_all(client_socket, 4)
        message_size = struct.unpack("L", message_size_data)[0]

        # Odbieranie danych
        data = receive_all(client_socket, message_size)

        # Obsługa wideo
        if prefix == b"VIDEO":
            try:
                frame = pickle.loads(data)
                if frame is not None:
                    cv2.imshow("Receiver: Video", frame)
                    print("Otrzymano obraz...")
                else:
                    print("Błąd: Otrzymano pusty obraz")
            except pickle.UnpicklingError:
                print("Błąd: Nie udało się odczytać obrazu. Dane mogą być uszkodzone.")
                break

        # Obsługa audio
        elif prefix == b"AUDIO":
            print(data)
            stream.write(data)  # Odtwarzanie odebranego dźwięku

except Exception as e:
    print(f"Błąd: {e}")

# Zwolnienie zasobów
client_socket.close()
cv2.destroyAllWindows()
stream.stop_stream()
stream.close()
audio.terminate()
