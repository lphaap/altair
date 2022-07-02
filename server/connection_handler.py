import socket as sockets;
import json as json;
import threading as threading;
import selectors as selectors;
import types as types;
import time as time;
import queue as queue;
from authenticator import Authenticator;
from origin_enum import Origin;
from typing import Union;

import sys
sys.path.append("..") #Dynamic import FIXME
from common import crypt as crypt;
from common import logger as logger;
from common.connection import Connection;

# Class for handling multiple client connections
class ConnectionHandler:

    def __init__(self, host_ip: str, host_port: str) -> None:
        self.host_ip = host_ip; # Ip for hosting socket server
        self.host_port = host_port; # Port for hosting socket server
        self.active = False; # Listen for connections or not
        self.connections = {}; # Active connections as Connection objects
        self.event_listener = selectors.DefaultSelector(); # Socket event listener
        self.authenticator = Authenticator(); # Authenticator for user connections
        self.server_socket = None; # Server socket for easy access
        self.msg_queue = queue.Queue(); # Command queue for processor to process

        # Test crypt module config files
        try:
            crypt.files_exist();
        except FileNotFoundError:
            logger.log("ERROR: Could not load crypt-module config files!");
            sys.exit(1);

        logger.log("ConnectionHandler - Init");


    # Start listening for client connections
    def listen(self) -> None:
        self.active = True;
        with sockets.socket(sockets.AF_INET, sockets.SOCK_STREAM) as server_socket:

            server_socket.bind((self.host_ip, self.host_port));
            server_socket.listen();
            server_socket.setblocking(False);
            self.server_socket = server_socket;

            self.event_listener.register(server_socket, selectors.EVENT_READ, data = None);
            logger.log("ConnectionHandler - Connection Listener started");

            while self.active:
                new_events = self.event_listener.select(timeout = 1); # Blocking selector waiting for events
                for source, event_mask in new_events:
                    if source.data is None: # Event came from a Server socket
                        self.add_connection(source.fileobj);
                    else: # Event came from a Client socket
                        self.handle_connection_event(source.fileobj, source.data.client_id, event_mask);

            logger.log("ConnectionHandler - Closing Listener loop");


    # Register a new client connection
    def add_connection(self, client_socket: sockets.socket) -> None:
        client_connection, client_address = client_socket.accept();
        client_connection.setblocking(False);

        logger.log(
            "ConnectionHandler - New Connection "
            + str(client_address[0])
            + ":" + str(client_address[1])
        );

        # Save client as a Connection obj
        client_id = self.parse_client_id(client_address[0], client_address[1]);
        client_obj = Connection(client_id, client_connection);
        self.connections[client_id] = client_obj;

        # Register listening format for client connection
        data_format = types.SimpleNamespace(
            client_address = client_address,
            client_id = client_id,
        );
        possible_events = selectors.EVENT_READ | selectors.EVENT_WRITE;

        self.event_listener.register(
            client_connection,
            possible_events,
            data_format
        );


    # Handle inputs sent from client connections
    def handle_connection_event(
        self,
        client_socket: sockets.socket,
        client_id: str,
        event_mask: int
    ) -> None:
        if event_mask & selectors.EVENT_READ:
            try:
                raw_data = client_socket.recv(4094);
            except (ConnectionAbortedError, ConnectionResetError) as exception:
                raw_data = None;

            if not raw_data:
                logger.log("ConnectionHandler - Connection reset: " + client_id);
                self.shutdown_connection(client_id);
                return;

            decrypted_data = crypt.decrypt(raw_data);
            parsed_data = json.loads(decrypted_data);

            client_connection = self.connections[client_id];
            if not client_connection:
                return; #FIXME Kill the connection?

            if not client_connection.is_authenticated():
                logger.log("ConnectionHandler - Authenticating client: " + client_id);

                # Authenticate the connection
                if not self.authenticate_connection(client_connection, parsed_data):
                    logger.log("ConnectionHandler - Authentication failure: " + client_id);
                    return self.shutdown_connection(client_id); # Shutdown on failure

                logger.log("ConnectionHandler - Authentication success: " + client_id);
                return; # Return since this message was for authentication

            logger.log("ConnectionHandler - New message from " + client_id + ": " + decrypted_data);

            # Append the message to message queue
            self.msg_queue.put(
                self.add_connection_headers(client_connection, parsed_data)
            );


    # Return next message from the queue, or None on empty
    def next_message(self) -> Union[dict, None]:
        if not self.msg_queue.empty():
            return self.msg_queue.get();

        return None;


    # Authenticate the connection, applies result to obj
    def authenticate_connection(self, connection: Connection, auth_package: dict) -> bool:
        # Validate auth package
        try:
            cmd = auth_package['cmd'];
            user = auth_package['user'];
            password = auth_package['password'];
        except AttributeError:
            return False;

        # Validate auth header
        if (cmd != self.authenticator.authentication_header):
            return False;

        # Validate user and password
        if (not self.authenticator.authenticate(user, password)):
            return False;

        # Authenticate connection and possible admin rights
        connection.authenticate(
            self.authenticator.authenticate_admin(user, password) # Give admin rights or not
        );
        connection.set_name(auth_package['name'] or connection.client_id);

        return True;


    # Add connection related headers used later in processing
    def add_connection_headers(self, connection: Connection, parsed_data: dict) -> dict:

        # Add connection origin, id and name to command
        parsed_data["origin"] = Origin.CLIENT;
        if connection.is_admin():
            parsed_data["origin"] = Origin.ADMIN;

        parsed_data["origin_id"] = connection.get_id();
        parsed_data["origin_name"] = connection.get_name();

        return parsed_data;


    # Encrypt and send a message to the designated client
    def send_to(self, client_id: str, msg_json: dict) -> bool:
        connection = self.connections[client_id];

        # Validate connection pre sending
        if not connection:
            return False;

        if not connection.is_active():
            return False;

        if not connection.is_authenticated():
            return False;

        json_data = json.dumps(msg_json, indent=4);
        logger.log("ConnectionHandler - Sending message to: " + client_id + ": " + json_data);
        encrypted_data = crypt.encrypt(json_data, False);
        res = connection.send(encrypted_data);

        # Kill connection if an error occurs
        if not res:
            self.shutdown_connection(client_id);
            return False;

        return True;

    # Brodcast given json message to all clients
    def send_broadcast(self, msg_json: dict) -> None:
        for client_id in self.get_active_connection_ids():
            self.send_to(client_id, msg_json);


    # Try to shutdown client connection gracefully
    def shutdown_connection(self, client_id: str) -> None:
        connection = self.connections[client_id];
        if not connection:
            return;

        logger.log("ConnectionHandler - Closing connection: " + connection.get_id());
        self.event_listener.unregister(connection.get_socket());
        connection.shutdown();
        del self.connections[connection.get_id()];


    # Try to shutdown client connection gracefully
    def shutdown_server(self) -> None:
        socket = self.server_socket;
        if not socket:
            return;

        self.event_listener.unregister(socket);
        socket.close();
        self.server_socket = None;


    # Try to shutdown all connections gracefully
    def shutdown(self) -> None:
        self.active = False;
        time.sleep(1); # Wait for listener to shutdown
        self.shutdown_server();

        # Close all client connections
        for client_id in self.get_active_connection_ids():
            self.shutdown_connection(client_id);

        logger.log("ConnectionHandler - Gracefull shutdown complete");


    # Is the handler listening for connections
    def is_active(self) -> bool:
        return self.active;


    # Parse client_id based on source ip and port
    def parse_client_id(self, client_ip: str, client_port: int) -> str:
        return str(client_ip).replace(".", "") + str(client_port);


    # Return an array of active connection ids
    def get_active_connection_ids(self) -> None:
        return self.connections.copy().keys();

    # Return client name, id and origin
    def get_client_info(self, client_id: str) -> None:
        connection = self.connections[client_id];
        if not connection:
            return None;

        return {
            "name": connection.get_name(),
            "id": connection.get_id(),
            "origin": Origin.ADMIN if connection.is_admin() else Origin.CLIENT,
            "ip": connection.get_ip(),
            "port": connection.get_port(),
        };