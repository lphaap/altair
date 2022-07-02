from datetime import datetime;

# Log given msg, persist param saves log
def log( msg: str, persistent: bool = False) -> None:

    if(type(msg) is not str):
        return;

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S");
    print(timestamp + ": " + msg);