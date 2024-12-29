import socket
import tkinter as tk
import cv2
import pickle
import struct
import pyaudio
import threading
import json



# Function to load configuration from the config.json file
def load_config():
    """
    Load the server's IP address and port from config.json.
    """
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
            ip_addr = config.get("Server_ip", "")
            port = config["Server_port"]
            return ip_addr, port
    except FileNotFoundError:
        print("config.json file not found.")
        return "", 1234
    except json.JSONDecodeError:
        print("Error decoding JSON from config.json.")
        return "", 1234
    
# Function to check the validity of the IP address and port
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


# Function to send audio
def send_audio(client_socket, stream, chunk):
    while True:
        try:
            audio_data = stream.read(chunk)
            audio_message_size = struct.pack("L", len(audio_data))
            client_socket.sendall(b"AUDIO" + audio_message_size + audio_data)
        except Exception as e:
            print(f"Error while sending audio: {e}")
            break


# Function to send video
def send_video(client_socket, cap):
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture video frame!")
                break

            # Display video locally
            cv2.imshow("Camera Preview", frame)

            # Serialize the frame
            data = pickle.dumps(frame)
            message_size = struct.pack("L", len(data))

            # Send the frame to the server
            client_socket.sendall(b"VIDEO" + message_size + data)

            # Exit on ESC key
            if cv2.waitKey(1) & 0xFF == 27:
                break
    except Exception as e:
        print(f"Error while sending video: {e}")


# Function to connect to the server and start streaming
# def connect(root):
#     ip_addr, port = load_config()
#     tk.Label(root, text="IP Address:").pack(pady=5)
#     ip_entry = tk.Entry(root)
#     ip_entry.pack(pady=5)

#     tk.Label(root, text="Port:").pack(pady=5)
#     port_entry = tk.Entry(root)
#     port_entry.pack(pady=5)

#     def on_button_click():
#         ip_addr = ip_entry.get()
#         port = port_entry.get()

#         if check_correctness(ip_addr, port):
#             HOST = ip_addr
#             PORT = int(port)

#             try:
#                 # Create and connect the client socket
#                 client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 client_socket.connect((HOST, PORT))
#                 print("Connected to the server!")

#                 # Open camera
#                 cap = cv2.VideoCapture(0)
#                 if not cap.isOpened():
#                     print("Error: Unable to access the camera.")
#                     return

#                 # Configure microphone
#                 CHUNK = 1024
#                 FORMAT = pyaudio.paInt16
#                 CHANNELS = 1
#                 RATE = 44100

#                 audio = pyaudio.PyAudio()
#                 stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

#                 # Start threads for audio and video streaming
#                 audio_thread = threading.Thread(target=send_audio, args=(client_socket, stream, CHUNK))
#                 audio_thread.daemon = True
#                 audio_thread.start()

#                 send_video(client_socket, cap)

#                 # Release resources after streaming ends
#                 cap.release()
#                 cv2.destroyAllWindows()
#                 stream.stop_stream()
#                 stream.close()
#                 audio.terminate()
#                 client_socket.close()

#             except Exception as e:
#                 print(f"Error during connection or streaming: {e}")

#     button = tk.Button(root, text="Connect", command=on_button_click)
#     button.pack(pady=20)
def connect(root):
    # Load configuration from config.json
    ip_addr, port = load_config()
    print(ip_addr)
    print(port)
    if not ip_addr or not port:
        print("Error: Invalid IP or port in config.json.")
        return

    print(f"Connecting to {ip_addr}:{port}")

    try:
        # Create and connect the client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip_addr, port))
        print("Connected to the server!")

        # Open camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Unable to access the camera.")
            return

        # Configure microphone
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        # Start threads for audio and video streaming
        audio_thread = threading.Thread(target=send_audio, args=(client_socket, stream, CHUNK))
        audio_thread.daemon = True
        audio_thread.start()

        send_video(client_socket, cap)

        # Release resources after streaming ends
        cap.release()
        cv2.destroyAllWindows()
        stream.stop_stream()
        stream.close()
        audio.terminate()
        client_socket.close()

    except Exception as e:
        print(f"Error during connection or streaming: {e}")


# Initialize the GUI
def init():
    root = tk.Tk()
    root.title("Budget Skype")
    root.geometry("600x400")
    connect(root)
    return root


def main():
    root = init()
    root.mainloop()


if __name__ == "__main__":
    main()
