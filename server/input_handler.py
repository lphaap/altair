import json as json;
import threading as threading;
import time as time;
import queue as queue;
from typing import Union;
from origin_enum import Origin;
from connection_handler import ConnectionHandler;

import sys
sys.path.append(".."); #Dynamic import FIXME
from common import logger as logger;

# Main class for processing commands received from active connections
class InputHandler:

    def __init__(self) -> None:
        logger.log("InputHandler - Init");
        self.active = False;
        self.msg_queue = queue.Queue(); # Command queue for processor to process

    # Start server-side input listener
    def listen(self) -> None:
        logger.log("InputHandler - Input Listener started");

        self.active = True;
        while self.active:
            try:
                command_input = input();
                command_json = {
                    "cmd": command_input,
                    "origin": Origin.SERVER,
                    "origin_name": "server-input",
                    "origin_id": "input-handler"
                };
                logger.log("InputHandler - Received command: " + command_json["cmd"]);
                self.msg_queue.put(command_json);
            except (KeyboardInterrupt, EOFError):
                continue;

        logger.log("InputHandler - Closing Listener loop");


    # Return next message from the queue, or None on empty
    def next_message(self) -> Union[dict, None]:
        if not self.msg_queue.empty():
            return self.msg_queue.get();

        return None;


    # Shutdown input thread
    def shutdown(self) -> None:
        logger.log("InputHandler - Closing Input Listener");
        self.active = False;
        logger.log("InputHandler - Gracefull shutdown complete");
