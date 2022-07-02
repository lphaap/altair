import json as json;
import threading as threading;
import time as time;
import queue as queue;
from origin_enum import Origin, origin_to_str;
from input_handler import InputHandler;
from connection_handler import ConnectionHandler;


import sys
sys.path.append(".."); #Dynamic import FIXME
from common import logger as logger;


# Main class for processing commands received from active connections
class Processor:

    def __init__(self) -> None:
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
                config["host_ip"],
                int(config["host_port"])
            );
            self.input_handler = InputHandler();
            self.enable_input_handler = config["enable_input_handler"];
        except KeyError:
            logger.log("ERROR: Config file missing key variables!");
            sys.exit();

    # Start up server and required threads
    def start(self) -> None:
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
    def stop(self) -> None:
        logger.log("Processor - Stopping all server threads");
        self.input_handler.shutdown();
        self.connection_handler.shutdown();
        self.shutdown_queue_processor();
        #time.sleep(1); # Wait for Queue processor shutdown
        logger.log("Processor - Gracefull shutdown complete");


    # Restarts server instance
    def restart(self) -> None:
        logger.log("Processor - Initiating Server restart");
        self.stop();
        logger.log("\n\n-------------------------- RESTART EVENT --------------------------\n");
        logger.log("Processor - Restarting Server threads");
        self.start();


    # Validate json command for processing
    def validate_command(self, json_input: dict) -> bool:

        if (
            not json_input
            or not json_input.get("cmd", False)
        ):
            return False;

        if (
            not json_input.get("origin", False)
            or not json_input.get("origin_id", False)
            or not json_input.get("origin_name", False)
        ):
            return False;

        return True;


    # Threadable function for processing command queue
    def start_queue_processor(self) -> None:
        self.queue_active = True;
        logger.log("Processor - Queue listener started");
        while self.queue_active:
            time.sleep(0.01); # Sleep 1ms to save resources FIXME Remove?

            # Fetch next manual command from InputHandler and process it if available
            manual_cmd = self.input_handler.next_message();
            if self.validate_command(manual_cmd):
                self.handle_command(manual_cmd);
                continue; # Found a valid command continue

            # Fetch next client command and process it if available
            client_cmd = self.connection_handler.next_message();
            if self.validate_command(client_cmd):
                self.handle_command(client_cmd);
                logger.log("valid2")
                continue; # Found a valid command continue

    # Shutdown queue processor thread
    def shutdown_queue_processor(self) -> None:
        self.queue_active = False;
        logger.log("Processor - Closing Queue listener");


    # Handle new command based on the origin
    # See commands.md for details
    def handle_command(self, json_input: dict) -> None:
        logger.log(
            "Processor - Processing command: " + json_input["cmd"]
            + ", Origin: "
            + origin_to_str(json_input["origin"])
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


    # All available Client commands
    # See commands.md for details
    def handle_client_command(self, json_input: dict) -> None:
        match json_input["cmd"]:

            case "clients":
                clients = [];
                for index, client_id in enumerate(
                    self.connection_handler.get_active_connection_ids()
                ):
                    client_info = self.connection_handler.get_client_info(client_id);
                    if (
                        not client_info
                        or client_info["id"] == json_input["origin_id"]
                    ):
                        continue;

                    clients.append({"name": client_info["name"]});

                return self.connection_handler.send_to(
                    json_input["origin_id"],
                    {
                        "cmd": "message",
                        "clients": clients,
                    }
                );


    # All available Admin commands
    # See commands.md for details
    def handle_admin_command(self, json_input: dict) -> None:
        match json_input["cmd"]:

            case "clients":
                clients = [];
                for index, client_id in enumerate(
                    self.connection_handler.get_active_connection_ids()
                ):
                    client_info = self.connection_handler.get_client_info(client_id);
                    if (
                        not client_info
                        or client_info["id"] == json_input["origin_id"]
                    ):
                        continue;

                    clients.append(
                        {
                            "id": client_info["id"],
                            "name": client_info["name"],
                            "ip": client_info["ip"],
                            "port": client_info["port"],
                            "origin": origin_to_str(client_info["origin"]),
                        }
                    );

                return self.connection_handler.send_to(
                    json_input["origin_id"],
                    {
                        "cmd": "message",
                        "clients": clients,
                    }
                );


            # Admins can access client commands
            case _:
                return self.handle_client_command(json_input);


    # All available Server commands
    # See commands.md for details
    def handle_server_command(self, json_input: dict) -> None:
        match json_input["cmd"]:

            case "shutdown":
                return self.stop();

            case "restart":
                return self.restart();

            case "clients":
                re = "\n\nCURRENTLY ACTIVE CONNECTIONS:\n";
                for index, client_id in enumerate(
                    self.connection_handler.get_active_connection_ids()
                ):
                    client_info = self.connection_handler.get_client_info(client_id)
                    if not client_info:
                        continue;

                    re = "".join([
                        re,
                        client_info["name"],
                        " - ",
                        origin_to_str(client_info["origin"]),
                        "@",
                        client_info["id"],
                        "\n"
                    ]);

                if not self.connection_handler.get_active_connection_ids():
                    re = re + "None";

                return logger.log(re);