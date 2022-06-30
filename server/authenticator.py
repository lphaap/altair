
class Authenticator:
    authentication_header = "authenticate";

    def __init__(self):
        return;

    def authenticate(self, username, password):
        return True;

    def authenticate_admin(self, username, password):
        return True;