#include <stdio.h>
#include <winsock2.h>
#include <windows.h>

#pragma comment(lib, "ws2_32.lib")

#define SERVER_IP "127.0.0.1"  // Adres IP serwera
#define SERVER_PORT 9999       // Port serwera
#define BUFFER_SIZE 1024       // Rozmiar bufora danych

int main() {
    WSADATA wsa;
    SOCKET client_socket;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    int bytes_sent, bytes_received;

    // Inicjalizacja WinSock
    printf("Inicjalizacja WinSock...\n");
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        printf("Inicjalizacja WinSock nie powiodła się. Kod błędu: %d\n", WSAGetLastError());
        return 1;
    }

    // Utworzenie gniazda
    client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket == INVALID_SOCKET) {
        printf("Nie można utworzyć gniazda. Kod błędu: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }
    printf("Gniazdo utworzone.\n");

    // Konfiguracja adresu serwera
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);

    // Połączenie z serwerem
    printf("laczenie z serwerem %s:%d...\n", SERVER_IP, SERVER_PORT);
    while(connect(client_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        printf("Polaczenie nie powiodlo sie. Kod bledu: %d\n", WSAGetLastError());
        closesocket(client_socket);
        WSACleanup();
        Sleep(1000);
    }
    printf("Połączono z serwerem.\n");

    // Wysyłanie danych do serwera
    printf("Wpisz wiadomość do wysłania: ");
    fgets(buffer, BUFFER_SIZE, stdin);
    buffer[strcspn(buffer, "\n")] = 0;  // Usunięcie znaku nowej linii

    bytes_sent = send(client_socket, buffer, strlen(buffer), 0);
    if (bytes_sent == SOCKET_ERROR) {
        printf("Wysyłanie nie powiodło się. Kod błędu: %d\n", WSAGetLastError());
    } else {
        printf("Wysłano %d bajtów.\n", bytes_sent);
    }

    // Odbieranie odpowiedzi od serwera
    bytes_received = recv(client_socket, buffer, BUFFER_SIZE, 0);
    if (bytes_received == SOCKET_ERROR) {
        printf("Odbieranie nie powiodło się. Kod błędu: %d\n", WSAGetLastError());
    } else {
        buffer[bytes_received] = '\0';  // Zakończenie ciągu
        printf("Otrzymano odpowiedź: %s\n", buffer);
    }

    // Zamknięcie połączenia
    closesocket(client_socket);
    WSACleanup();
    printf("Połączenie zamknięte.\n");

    return 0;
}
