import json as json;
from connection_handler import ConnectionHandler;
import threading as threading;
import time as time;
from origin_enum import Origin;

import sys
sys.path.append(".."); #Dynamic import FIXME
from common import logger as logger;

# Main class for processing commands received from active connections
class InputHandler:

    def __init__(self, processor):
        logger.log("InputHandler - Init");
        self.active = False;
        self.processor = processor;


    # Start server-side input listener
    def listen(self):
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
                self.processor.process(command_json);
            except (KeyboardInterrupt, EOFError):
                continue;

        logger.log("InputHandler - Closing Listener loop");


    # Shutdown input thread
    def shutdown(self):
        logger.log("InputHandler - Closing Input Listener");
        self.active = False;
        logger.log("InputHandler - Gracefull shutdown complete");
