import socket as sockets;
import json as json;
import time as time;
from datetime import datetime;
import selectors as selectors;
import threading as threading;
import types as types;

import sys;
sys.path.append(".."); #Dynamic import FIXME
from common import crypt as crypt;
from common import logger as logger;
from common.connection import Connection;

class ConnectionHandler:

    SERVER_ID = "server-connection";

    def __init__(self) -> None:
        self.server_ip = "127.0.0.1"; # Ip for hosting socket server FIXME Get from config
        self.server_port = 55555; # Port for hosting socket server FIXME Get from config
        self.active = False; # Listen for connections or not
        self.server_connection = None; # Active connections as Connection objects
        self.event_listener = selectors.DefaultSelector(); # Socket event listener
        logger.log("ConnectionHandler - Init");

    # Start listening for client connections
    def connect_to_server(self) -> None:
        server_address = (self.server_ip, self.server_port);
        server_socket = sockets.socket(sockets.AF_INET, sockets.SOCK_STREAM);
        server_socket.setblocking(False);
        server_socket.connect_ex(server_address);
        self.server_connection = Connection(self.SERVER_ID, server_socket);
        self.server_connection.authenticate(); # Set authentication flag just in case

        possible_events = selectors.EVENT_READ | selectors.EVENT_WRITE;

        data_format = types.SimpleNamespace(
            client_id = self.SERVER_ID,
        );

        self.event_listener.register(
            server_socket,
            possible_events,
            data_format,
        );

        # Init event listener if not already active
        if not self.active:
            threading.Thread(target = self.listen).start();
            time.sleep(1);

        auth_package = {
            "cmd": "authenticate",
            "user": "user123",
            "password": "pass123",
            "name": "local_user",
        };
        self.send_to_server(auth_package);


    # Try to gracefully shutdown server connection
    def shutdown_server_connection(self) -> None:
        if not self.server_connection.is_active():
            return;

        self.event_listener.unregister(self.server_connection.get_socket());
        self.server_connection.shutdown();
        logger.log("ConnectionHandler - Closing server connection");


    # Listen for registered socket events
    def listen(self) -> None:
        logger.log("ConnectionHandler - Listener started");
        self.active = True;
        while self.active:

            # FIXME Check for multiple connections when implemented
            if not self.server_connection.is_active():
                self.shutdown();
                continue;

            new_events = self.event_listener.select(timeout = 1); # Blocking selector waiting for events
            for source, event_mask in new_events:
                self.handle_connection_event(source.fileobj, source.data.client_id, event_mask);

        logger.log("ConnectionHandler - Closing Listener loop");


    # Handle events from event_listener
    def handle_connection_event(
        self,
        socket: sockets.socket,
        client_id: str,
        event_mask: int
    ) -> None:
        if event_mask & selectors.EVENT_READ:
            try:
                raw_data = socket.recv(4094);
            except (ConnectionAbortedError, ConnectionResetError) as exception:
                raw_data = None;

            if not raw_data:
                logger.log("ConnectionHandler - Connection Reset: " + client_id);
                if client_id == self.SERVER_ID:
                    self.shutdown_server_connection();
                return;

            decrypted_data = crypt.decrypt(raw_data);
            parsed_data = json.loads(decrypted_data);
            logger.log("ConnectionHandler - Received data: " + decrypted_data + ", from: " + client_id);

            #FIXME: Move to event handler
            if parsed_data['cmd'] == "shutdown":
                self.shutdown();


    # Try to send json payload to server
    def send_to_server(self, msg_json: dict) -> None:
        if not self.server_connection.is_active():
            return;

        json_data = json.dumps(msg_json, indent=4);
        logger.log("ConnectionHandler - Sending message to server: " + json_data);
        encrypted_data = crypt.encrypt(json_data, False);
        res = self.server_connection.send(encrypted_data);

        if not res:
            self.shutdown_server_connection();


    # Try to gracefully shutdown all connections
    def shutdown(self) -> None:
        if not self.active:
            return;

        self.active = False;
        time.sleep(1); # Wait for listener to shutdown

        # Close server connection
        if self.server_connection.is_active():
            self.shutdown_server_connection();

        logger.log("ConnectionHandler - Gracefull shutdown complete");





