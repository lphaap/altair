import base64;
import os;
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def encrypt(payload, re_string = True):
    fernet = init_fernet();
    
    if type(payload) is str:
        payload = bytes(payload, encoding='utf-8');
        
    if type(payload) is not bytes:
        raise TypeError("Payload not in bytes or string")
    
    encrypted_payload = fernet.encrypt(payload);
    
    if re_string:
        return encrypted_payload.decode(encoding='utf-8');
    
    return encrypted_payload;
    
    
def decrypt(payload, re_string = True):
    fernet = init_fernet();
    
    if type(payload) is str:
        payload = bytes(payload, encoding='utf-8');
        
    if type(payload) is not bytes:
        raise TypeError("Payload not in bytes or string");
    
    decrypted_payload = fernet.decrypt(payload);
    
    if re_string:
        return decrypted_payload.decode(encoding='utf-8');
    
    return decrypted_payload;

def init_fernet():
    
    auth_path = os.path.join(os.path.dirname(__file__), "auth");
    
    password = bytes(
        open(os.path.join(auth_path, "pass.key")).read(), 
        encoding='utf-8'
    );
    
    salt = bytes(
        open(os.path.join(auth_path, "salt.key")).read(), 
        encoding='utf-8'
    );
    
    scrambler = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=400000,
    );
    
    encryption_key = base64.urlsafe_b64encode(
        scrambler.derive(password)
    );
    
    return Fernet(encryption_key);