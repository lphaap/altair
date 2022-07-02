from common import logger as logger;
from typing import Union;
import socket as sockets;

# A Class to conviniently store connection data in one spot
class Connection:

    def __init__(self, id: str, socket: sockets.socket) -> None:
        self.socket = socket;
        self.id = id;
        self.name = id;
        self.active = True;
        self.authenticated = False;
        self.admin = False;
        self.ip = socket.getpeername()[0];
        self.port = socket.getpeername()[1];

    # Shutdown socket connection
    def shutdown(self) -> None:
        self.active = False;
        try:
            self.socket.close();
        except ConnectionAbortedError: # Socket already closed
            logger.log("Got ConnectionAbortedError while closing connection: " + self.id);
            return;

    # Is this connection alive
    def is_active(self) -> bool:
        return self.active;

    # Is this connection authenticated
    def is_authenticated(self) -> bool:
        return self.authenticated;

    # Is this connection an admin connection
    def is_admin(self) -> bool:
        return self.admin;

    # Authenticate this connection
    def authenticate(self, is_admin: bool = False) -> None:
        self.authenticated = True;
        self.admin = is_admin;

    # Directly sends the raw text given to the client
    def send(self, msg: str) -> bool:
        try:
            self.socket.sendall(msg);
            return True;
        except ConnectionAbortedError: # Socket already closed
            logger.log("Got ConnectionAbortedError while sending message to: " + self.id);
            return False;


    #--- Getters & Setters ---#

    def get_name(self) -> str:
        return self.name;

    def set_name(self, name: str) -> None:
        self.name = name;
        return;

    def get_id(self) -> str:
        return self.id;

    def get_ip(self) -> str:
        return self.ip;

    def get_port(self) -> str:
        return self.port;

    def get_socket(self) -> str:
        return self.socket;
