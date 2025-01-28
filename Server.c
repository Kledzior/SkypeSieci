#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/epoll.h>
#include <errno.h>

#define MAX_EVENTS 10
#define BUFFER_SIZE 10240
#define PORT 8880
#define MAX_NICK_LENGTH 100


void handle_error(const char *message) {
    perror(message);
    exit(EXIT_FAILURE);
}

void broadcast_to_clients(int sender_fd, int *clients, int client_count, char *data, ssize_t size) {
    for (int i = 0; i < client_count; i++) {
        if (clients[i] != sender_fd && clients[i] != -1) {
            if (send(clients[i], data, size, 0) == -1) {
                perror("send failed");
                close(clients[i]);
                clients[i] = -1; // Oznacz klienta jako rozłączonego
            }
        }
    }
}

int find_client_by_nick(const char *nick, char client_nicks[MAX_EVENTS][MAX_NICK_LENGTH], int *clients) {
    for (int i = 0; i < MAX_EVENTS; i++) {
        if (clients[i] != -1 && strcmp(client_nicks[i], nick) == 0) {
            return i;
        }
    }
    return -1;
}

int is_friend_connection_valid(int client_index, char client_nicks[MAX_EVENTS][MAX_NICK_LENGTH], char friend_nicks[MAX_EVENTS][MAX_NICK_LENGTH], int *clients) {
    if (strcmp(friend_nicks[client_index], "") == 0) {
        return 0; // No friend specified
    }

    int friend_index = find_client_by_nick(friend_nicks[client_index], client_nicks, clients);
    if (friend_index == -1 || clients[friend_index] == -1) {
        return 0; // Friend not connected
    }

    if (strcmp(friend_nicks[friend_index], client_nicks[client_index]) != 0) {
        return 0; // Friendship not mutual
    }

    return 1; // Valid connection
}

int main() {
    int server_fd, epoll_fd, client_fd, event_count, i;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_addr_len = sizeof(client_addr);
    struct epoll_event event, events[MAX_EVENTS];
    char buffer[BUFFER_SIZE];
    int clients[MAX_EVENTS] = { -1 }; // Tablica klientów
    char client_nicks[MAX_EVENTS][MAX_NICK_LENGTH]; // Tablica nicków
    char friend_nicks[MAX_EVENTS][MAX_NICK_LENGTH] = { "" }; // Tablica przyjaciół

    // Tworzenie gniazda serwera
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1)
        handle_error("Socket creation failed");

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) == -1)
        handle_error("setsockopt failed");

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1)
        handle_error("Bind failed");

    if (listen(server_fd, 10) == -1)
        handle_error("Listen failed");

    epoll_fd = epoll_create1(0);
    if (epoll_fd == -1)
        handle_error("epoll_create1 failed");

    event.events = EPOLLIN;
    event.data.fd = server_fd;
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, server_fd, &event) == -1)
        handle_error("epoll_ctl failed");

    printf("Serwer nasłuchuje na porcie %d...\n", PORT);

    while (1) {
        event_count = epoll_wait(epoll_fd, events, MAX_EVENTS, -1);
        if (event_count == -1)
            handle_error("epoll_wait failed");

        for (i = 0; i < event_count; i++) {
            if (events[i].data.fd == server_fd) {
                client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_addr_len);
                if (client_fd == -1) {
                    perror("accept failed");
                    continue;
                }

                printf("Nowe połączenie od %s:%d (fd: %d)\n",
                       inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port), client_fd);

                char nick[MAX_NICK_LENGTH];
                ssize_t bytes_received = recv(client_fd, nick, sizeof(nick), 0);
                if (bytes_received <= 0) {
                    printf("Błąd odbierania nicku.\n");
                    close(client_fd);
                    continue;
                }

                nick[strcspn(nick, "\n")] = '\0';  // Usuń znak nowej linii
                printf("Nick klienta: %s\n", nick);

                // Dodanie klienta do listy
                int added = 0;
                int j;
                for (j = 0; j < MAX_EVENTS; j++) {
                    if (clients[j] == -1) {
                        clients[j] = client_fd;
                        strncpy(client_nicks[j], nick, MAX_NICK_LENGTH);

                        // Odbieranie nicka przyjaciela
                        bytes_received = recv(client_fd, friend_nicks[j], MAX_NICK_LENGTH, 0);
                        if (bytes_received > 0) {
                            friend_nicks[j][strcspn(friend_nicks[j], "\n")] = '\0';
                            printf("%s chce się połączyć z %s\n", nick, friend_nicks[j]);
                        } else {
                            printf("Błąd odbierania nicka przyjaciela dla %s\n", nick);
                            close(client_fd);
                            clients[j] = -1;
                        }

                        added = 1;
                        break;
                    }
                }

                if (!added) {
                    printf("Serwer pełny, odrzucenie klienta %s\n", nick);
                    close(client_fd);
                } else {
                    if(is_friend_connection_valid(j, client_nicks, friend_nicks, clients))
                    {
                        printf("Polaczenie niepoprawne");
                        break;
                    }
                    // Dodanie klienta do epolla
                    event.events = EPOLLIN;
                    event.data.fd = client_fd;
                    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &event) == -1)
                        handle_error("epoll_ctl failed for client_fd");

                    // Sprawdzenie poprawności połączenia
                    if (is_friend_connection_valid(j, client_nicks, friend_nicks, clients)) {
                        int friend_index = find_client_by_nick(friend_nicks[j], client_nicks, clients);
                        send(clients[friend_index], "Połączono z przyjacielem!", 25, 0);
                        send(client_fd, "Połączono z przyjacielem!", 25, 0);
                        printf("Połączono %s z %s\n", nick, friend_nicks[j]);
                    } else {
                        printf("%s czeka na połączenie z %s\n", nick, friend_nicks[j]);
                    }
                }

            } else {
                int client_fd = events[i].data.fd;
                ssize_t bytes_received = recv(client_fd, buffer, sizeof(buffer), 0);

                if (bytes_received <= 0) {
                    printf("Rozłączenie klienta (fd: %d)\n", client_fd);
                    close(client_fd);
                    epoll_ctl(epoll_fd, EPOLL_CTL_DEL, client_fd, NULL);
                    for (int j = 0; j < MAX_EVENTS; j++) {
                        if (clients[j] == client_fd) {
                            clients[j] = -1;
                            friend_nicks[j][0] = '\0'; // Reset friend nick
                            break;
                        }
                    }
                } else {
                    printf("Otrzymano dane (%ld bajtów) od klienta (fd: %d)\n", 
                           bytes_received, client_fd);
                    broadcast_to_clients(client_fd, clients, MAX_EVENTS, buffer, bytes_received);
                }
            }
        }
    }

    close(server_fd);
    close(epoll_fd);
    return 0;
}