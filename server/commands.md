# Server commands

## *shutdown*
*Shutdowns server and all server threads.*

## *restart*
*Restart server and all server threads. (Drops all client connections)*

## *clients*
*Log active clients with related information:*  

    name - ORIGIN@CLIENT_ID


# Admin commands
## *clients*
*Retrivies active clients with full information:*  

    "cmd": "message",
    "clients": [
        {  
            "id": "1234",
            "name": "client",
            "ip": "127.0.0.1",
            "port": "23232",
            "origin": "SERVER"
        }
    ]

# Client commands
## *clients*
*Retrieves active client names:*  

    "cmd": "message",
    "clients": [
        {  
            "name": "client",
        }
    ]