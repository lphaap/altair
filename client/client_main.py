from client_connection_handler import ConnectionHandler;
import time;
import threading;

import sys
sys.path.append("..") #Dynamic import FIXME
from common import logger as logger;

handler = ConnectionHandler();
thread = threading.Thread(target = handler.connect_to_server);
thread.start();
time.sleep(5);
#handler.send_to_server({
#    "cmd": "message",
#    "to": "12700158099",
#    "message": "Hello 123"
#});
handler.send_to_server({
    "cmd": "broadcast",
    "payload": {
        "cmd": "message",
        "message": "Hello 123"
    }
});
#time.sleep(5);
#logger.log("Main sleep done initializing shutdown");
#handler.shutdown();