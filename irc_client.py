import socket

class IRCClient:

    def __init__(self, server='192.168.1.5', port=1234):
        self.server = server
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.connection.connect((self.server, self.port))
        """
        self.connection.bind((self.server, self.port))
        self.connection.listen(2)
        self.conection, addr = self.connection.accept()"""

    def get_response(self):
        a = ''
        b = self.connection.recv(1).decode('utf-8')
        a = b
        while(b!='\n'):
            a +=b
            b = self.connection.recv(1).decode('utf-8')

        return a

    def send_cmd(self, cmd, message):
        command = "{} {}".format(cmd, message).encode("utf-8")
        self.connection.send(command)

    def join_channel(self, channel):
        cmd = "JOIN"
        self.send("{} {}".format(cmd, channel))

    def send_message(self, message):
        cmd = "MSSG"
        self.send("{} {}".format(cmd, message))

    def send(self, message):
        print(message)
        self.connection.send(message.encode('utf-8'))
