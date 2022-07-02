from enum import Enum, auto;
from typing import Union;

# Enum to map message categories based on command origin
class Origin(Enum):
    SERVER = auto();
    ADMIN = auto();
    CLIENT = auto();

def origin_to_str(origin: Origin) -> Union[str, None]:
    origin_to_str = {
        Origin.SERVER: "SERVER",
        Origin.ADMIN: "ADMIN",
        Origin.CLIENT: "CLIENT",
    };
    return origin_to_str[origin];