import socket
import cv2
import pickle
import struct
import pyaudio
import threading
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio-Video Client")

        # Zmienne stanu
        self.client_socket = None
        self.camera = None
        self.audio_stream = None
        self.running = False

        # Ustawienia audio
        self.CHUNK = 1024 * 10
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        
        self.build_login_screen()

    def clear_screen(self):
        """Usuwanie wszystkich widżetów z okna."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def build_login_screen(self):
        """Budowanie ekranu logowania."""
        self.clear_screen()

        tk.Label(self.root, text="Twój Nick:").pack(pady=5)
        self.nick_entry = tk.Entry(self.root)
        self.nick_entry.pack(pady=5)

        tk.Label(self.root, text="Nick osoby do połączenia:").pack(pady=5)
        self.friend_entry = tk.Entry(self.root)
        self.friend_entry.pack(pady=5)

        tk.Label(self.root, text="Adres IP serwera:").pack(pady=5)
        self.ip_entry = tk.Entry(self.root)
        self.ip_entry.insert(0, "192.168.177.245")
        self.ip_entry.pack(pady=5)

        tk.Label(self.root, text="Port serwera:").pack(pady=5)
        self.port_entry = tk.Entry(self.root)
        self.port_entry.insert(0, "8880")
        self.port_entry.pack(pady=5)

        tk.Button(self.root, text="Zaloguj się", command=self.connect_to_server).pack(pady=20)

    def connect_to_server(self):
        """Obsługa połączenia z serwerem."""
        try:
            server_ip = self.ip_entry.get()
            server_port = int(self.port_entry.get())
            nick = self.nick_entry.get()
            friend=self.friend_entry.get()

            # Połączenie z serwerem
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, server_port))

            # Wyślij swój nick
            self.client_socket.sendall(nick.encode('utf-8'))
            self.client_socket.sendall(friend.encode('utf-8'))

            # Uruchomienie kamery i audio jak poprzednio
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("Nie można otworzyć kamery.")

            audio = pyaudio.PyAudio()
            self.audio_stream = audio.open(
                format=self.FORMAT, 
                channels=self.CHANNELS, 
                rate=self.RATE, 
                input=True, 
                output=True,
                input_device_index=1, output_device_index=4,
                frames_per_buffer=self.CHUNK
            )

            self.build_camera_screen()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się połączyć z serwerem: {e}")

    def build_camera_screen(self):
        """Budowanie ekranu kamery."""
        self.clear_screen()

        # Miejsce na podgląd obrazu
        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        # Przycisk rozłączenia
        tk.Button(self.root, text="Rozłącz", command=self.disconnect).pack(pady=20)

        # Rozpoczęcie wątków do obsługi danych
        self.running = True
        threading.Thread(target=self.send_data, daemon=True).start()
        threading.Thread(target=self.receive_data, daemon=True).start()
        self.update_video_feed()

    def disconnect(self):
        """Rozłączenie i zwolnienie zasobów."""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.camera:
            self.camera.release()
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        cv2.destroyAllWindows()
        self.build_login_screen()

    def send_data(self):
        """Wysyłanie audio i wideo do serwera."""
        try:
            while self.running:
                # Odczyt audio
                audio_data = self.audio_stream.read(self.CHUNK)
                audio_message_size = struct.pack("L", len(audio_data))
                self.client_socket.sendall(b"AUDIO" + audio_message_size + audio_data)

                # Odczyt wideo
                ret, frame = self.camera.read()
                if not ret:
                    break

                # Kompresja i wysyłanie wideo
                _, buffer = cv2.imencode('.jpg', frame)
                frame_data = buffer.tobytes()
                frame_size = struct.pack("L", len(frame_data))
                self.client_socket.sendall(b"VIDEO" + frame_size + frame_data)
        except Exception as e:
            print(f"Błąd podczas wysyłania danych: {e}")

    def receive_data(self):
        """Odbieranie danych od serwera."""
        try:
            while self.running:
                prefix = self.receive_all(5)
                if prefix == b"AUDIO":
                    # Odbieranie audio
                    message_size_data = self.receive_all(4)
                    message_size = struct.unpack("L", message_size_data)[0]
                    audio_data = self.receive_all(message_size)
                    self.audio_stream.write(audio_data)

                elif prefix == b"VIDEO":
                    # Odbieranie wideo
                    frame_size_data = self.receive_all(4)
                    frame_size = struct.unpack("L", frame_size_data)[0]
                    frame_data = self.receive_all(frame_size)

                    # Dekodowanie obrazu i aktualizacja podglądu
                    frame_array = np.frombuffer(frame_data, np.uint8)
                    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                    self.current_frame = frame
        except Exception as e:
            print(f"Błąd podczas odbierania danych: {e}")

    def update_video_feed(self):
        """Aktualizowanie obrazu na ekranie."""
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (320, 240))
            img = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.video_label.imgtk = img
            self.video_label.configure(image=img)
        if self.running:
            self.root.after(10, self.update_video_feed)

    def receive_all(self, size):
        """Odbieranie dokładnie `size` bajtów."""
        data = b""
        while len(data) < size:
            packet = self.client_socket.recv(size - len(data))
            if not packet:
                raise ConnectionError("Połączenie zakończone przez serwer")
            data += packet
        return data

# Uruchomienie aplikacji
if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
