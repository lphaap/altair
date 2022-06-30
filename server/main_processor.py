import json as json;
from connection_handler import ConnectionHandler;
from input_handler import InputHandler;
import threading as threading;
import time as time;
import queue as queue;
from origin_enum import Origin;

import sys
sys.path.append(".."); #Dynamic import FIXME
from common import logger as logger;


# Main class for processing commands received from active connections
class Processor:

    def __init__(self):
        logger.log("Processor - Init");

        #Init FIFO Q
        self.cmd_queue = queue.Queue();
        self.queue_active = False;

        # Init server script and fail on invalid configs
        try:
            config = json.load(
                open("config/config.json")
            );
        except FileNotFoundError:
            logger.log("ERROR: Could not load server config file!");
            sys.exit();

        try:
            self.connection_handler = ConnectionHandler(
                self,
                config["host_ip"],
                int(config["host_port"])
            );
            self.input_handler = InputHandler(self);
            self.enable_input_handler = config["enable_input_handler"];
        except KeyError:
            logger.log("ERROR: Config file missing key variables!");
            sys.exit();

    # Start up server and required threads
    def start(self):
        logger.log("Processor - Starting all server threads");

        # CommandQueueProcessor start
        threading.Thread(
            target = self.start_queue_processor,
            daemon = False
        ).start();

        # Input handler start
        if self.enable_input_handler:
            threading.Thread(
                target = self.input_handler.listen,
                daemon = True
            ).start();
        else:
            logger.log("Processor - InputHandler disabled skipping");

        # ConnectionHandler start
        threading.Thread(
            target = self.connection_handler.listen,
            daemon = False
        ).start();


    # Cleanup and shutdown all threads
    def stop(self):
        logger.log("Processor - Stopping all server threads");
        self.input_handler.shutdown();
        self.connection_handler.shutdown();
        self.shutdown_queue_processor();
        #time.sleep(1); # Wait for Queue processor shutdown
        logger.log("Processor - Gracefull shutdown complete");


    # Process json commands
    def process(self, json_input):
        if (
            not json_input
            or not json_input.get("cmd", False)
        ):
            logger.log("Processor - Received empty command");
            return;

        if (
            not json_input.get("origin", False)
            or not json_input.get("origin_id", False)
            or not json_input.get("origin_name", False)
        ):
            logger.log("Processor - Received command without sender context");
            return;

        self.cmd_queue.put(json_input);

    # Threadable function for processing command queue
    def start_queue_processor(self):
        self.queue_active = True;
        logger.log("Processor - Queue listener started");
        while self.queue_active:
            if not self.cmd_queue.empty():
                self.handle_command(self.cmd_queue.get());
            time.sleep(0.01); # Sleep 1ms to save resources FIXME Remove?


    # Shutdown queue processor thread
    def shutdown_queue_processor(self):
        self.queue_active = False;
        logger.log("Processor - Closing Queue listener");


    # Handle new command based on the origin
    def handle_command(self, json_input):
        logger.log(
            "Processor - Processing command: " + json_input["cmd"]
            + ", Origin: "
            + Origin.to_str(json_input["origin"])
            + "@"
            + json_input["origin_id"]
        );

        match json_input["origin"]:
            case Origin.CLIENT:
                return self.handle_client_command(json_input);
            case Origin.ADMIN:
                return self.handle_admin_command(json_input);
            case Origin.SERVER:
                return self.handle_server_command(json_input);
            case _:
                return logger.log("Processor - Unexpected origin");

    # Restarts server instance
    def restart(self):
        logger.log("Processor - Initiating Server restart");
        self.stop();
        logger.log("\n\n-------------------------- RESTART EVENT --------------------------\n");
        logger.log("Processor - Restarting Server threads");
        self.start();


    # All available Client commands
    def handle_client_command(self, json_input):
        # TODO Client commands
        return;


    # All available Admin commands
    def handle_admin_command(self, json_input):
        # TODO Admin commands
        return self.handle_client_command(json_input); # Admins can access client commands


    # All available Server commands
    def handle_server_command(self, json_input):
        match json_input["cmd"]:

            # Shutdown server and all connections
            case "shutdown":
                return self.stop();

            # Restart server instance
            case "restart":
                return self.restart();

            # Log currently active client connections
            case "clients":
                re = "\n\nCURRENTLY ACTIVE CONNECTIONS:\n";
                for index, client_id in enumerate(self.connection_handler.get_active_connection_ids()):
                    client_info = self.connection_handler.get_client_info(client_id)

                    if not client_info:
                        continue;

                    re = "".join([
                        re,
                        client_info["name"],
                        " - ",
                        Origin.to_str(client_info["origin"]),
                        "@",
                        client_info["id"],
                        "\n"
                    ]);

                if not self.connection_handler.get_active_connection_ids():
                    re = re + "None";

                return logger.log(re);