#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/un.h>
#include <stdlib.h>

int main()
{
    int sfd,cfd;
    socklen_t sl;
    struct sockaddr_in saddr,caddr;

    memset(&saddr, 0 ,sizeof(saddr));
    saddr.sin_addr.s_addr = INADDR_ANY;
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(1234);

    sfd = socket(AF_INET,SOCK_STREAM,0);
    bind(sfd,(struct sockaddr*)&saddr,sizeof(saddr));
    listen(sfd,10);
    while(1)
    {
        sl = sizeof(caddr);
        cfd = accept(sfd, (struct sockaddr*)&caddr,&sl);
        if(!fork())
        {
            close(sfd);
            write(cfd,"Hello",5);
            sleep(5);
            write(1,"Closing Connection\n",20);
            close(cfd);
            exit(0);
        }
    }

}