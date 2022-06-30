from enum import Enum, auto;

# Enum to map message categories based on command origin 
class Origin(Enum):
    SERVER = auto();
    ADMIN = auto();
    CLIENT = auto();
    
    def to_str(origin) -> str:
        origin_to_str = {
            Origin.SERVER: "SERVER",
            Origin.ADMIN: "ADMIN",
            Origin.CLIENT: "CLIENT",
        };
        return origin_to_str[origin];