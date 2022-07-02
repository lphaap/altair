
class Authenticator:
    authentication_header = "authenticate";

    def __init__(self) -> None:
        return;

    def authenticate(self, username: str, password: str) -> bool:
        return True;

    def authenticate_admin(self, username: str, password: str) -> bool:
        return False;