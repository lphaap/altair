# Server commands

## *shutdown*
 - *Shutdowns server and all server threads.*
 - *Request: 'shutdown'*

## *restart*
 - Restart server and all server threads. (Drops all client connections)
 - *Request: 'restart'*

## *clients*
 - Log active clients with related information:*  
 - *Request: 'clients'*
 - *Response: 'name - ORIGIN@CLIENT_ID'*


# Admin commands
## *clients*
 - Retrivies active clients with full information  

*Request:*

    "cmd": "clients",

*Response:*

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

## *broadcast*
 - Broadcasts given payload to all clients  

*Request:*

    "cmd": "broadcast",
    "payload": {
        "cmd": "shutdown",
    }

# Client commands
## *clients*
- Retrieves active clients  

*Request:*

    "cmd": "clients",

*Response:*

    "cmd": "response",
    "clients": [
        {  
            "id": "client",
            "name": "client",
        }
    ]

## *message*
- Send message to specified receiver  

*Request:*

    "cmd": "message",
    "message": "Hello world",
    "to": "client_id"


# Errors
 - If an error occurs an error response is returned

## *Error*

    "cmd": "error",
    "source": "cmd_which_failed",
    "message": "Error description"