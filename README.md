Projekt umożliwia audio-wideo komunikację imitującą zachowanie Skype w czasie rzeczywistym między dwoma użytkownikami poprzez sieć lokalną (LAN).
Użytkownicy łączą się za pomocą własnych nicków i mogą komunikować się tylko wtedy, gdy obustronnie wskażą siebie jako przyjaciela oraz podadzą poprawny adres IP ora numer portu Servera.

Technologie użyte w projekcie
Klient (client.py)
Python 3

Tkinter — budowa interfejsu graficznego (GUI).

OpenCV (cv2) — obsługa obrazu z kamery i jego kompresja (JPEG).

PyAudio — przechwytywanie i odtwarzanie dźwięku.

Socket — komunikacja sieciowa TCP/IP.

Threading — równoległe przetwarzanie audio, wideo i GUI.

Serwer (server.c)
C

Sockets (sys/socket.h) — TCP/IP komunikacja sieciowa.

epoll (sys/epoll.h) — efektywne zarządzanie wieloma połączeniami klientów.

POSIX standard — zarządzanie gniazdami i zdarzeniami.

Linux API — niskopoziomowa obsługa połączeń sieciowych.
