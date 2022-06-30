from common import logger as logger;

# A Class to conviniently store connection data in one spot
class Connection:
    def __init__(self, id, socket):
        self.socket = socket;
        self.id = id;
        self.name = id;
        self.active = True;
        self.authenticated = False;
        self.admin = False;
        self.ip = socket.getpeername()[0];
        self.port = socket.getpeername()[1];

    # Shutdown socket connection
    def shutdown(self):
        self.active = False;
        try:
            self.socket.close();
        except ConnectionAbortedError: # Socket already closed
            logger.log("Got ConnectionAbortedError while closing connection: " + self.id);
            return;

    # Is this connection alive
    def is_active(self):
        return self.active;

    # Is this connection authenticated
    def is_authenticated(self):
        return self.authenticated;

    # Is this connection an admin connection
    def is_admin(self):
        return self.admin;

    # Authenticate this connection
    def authenticate(self, is_admin = False):
        self.authenticated = True;
        self.admin = is_admin;

    # Directly sends the raw text given to the client
    def send(self, msg):
        try:
            self.socket.sendall(msg);
            return True;
        except ConnectionAbortedError: # Socket already closed
            logger.log("Got ConnectionAbortedError while sending message to: " + self.id);
            return False;


    #--- Getters & Setters ---#

    def get_name(self):
        return self.name;

    def set_name(self, name):
        self.name = name;
        return self;

    def get_id(self):
        return self.id;

    def get_ip(self):
        return self.ip;

    def get_port(self):
        return self.port;

    def get_socket(self):
        return self.socket;
