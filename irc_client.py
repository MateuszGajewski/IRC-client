import socket

#Klasa implementująca komunikacje sieciową

class IRCClient:
    #Inicjalizajca gniazda sieciowego
    def __init__(self, server="127.0.0.1", port=1234):
        self.server = server
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.connection.settimeout(0.00001)
    #Połaczenie ze wskazanym serwerem przez wskazany port
    def connect(self):
        self.connection.connect((self.server, self.port))

    #Odbieranie wiadomości
    def get_response(self):
        a = ''
        try:
            b = self.connection.recv(1).decode('utf-8')
            a = b
            while(b!='\n'):
                a +=b
                b = self.connection.recv(1).decode('utf-8')


            return a
        except:
            pass


    #Wysyłanie wiadomości
    def send(self, message):
        try:
            i = 0
            while(message[i]!= '\n'):
                self.connection.send(message[i].encode('utf-8'))
                i+=1
            self.connection.send(message[i].encode('utf-8'))
        except:
            pass
