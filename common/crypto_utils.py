from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
import base64


def generateECKey():
    private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
    return private_key

def loadECKey(pem_data):
    try:
        private_key = load_pem_private_key(pem_data, password=None, backend=default_backend())
        return private_key
    except:
        return None

def loadPublicKey(pem_data):
    try:
        key = load_pem_public_key(pem_data, backend=default_backend())
        return key
    except:
        return None

def serializeECKey(private_key):
    data = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                                    encryption_algorithm=serialization.NoEncryption()
                                    )
    return data

def serializePublicKey(public_key):
    data = public_key.public_bytes(serialization.Encoding.PEM,
                                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                                    )
    return data

def sign(data, private_key):
    hash = hashes.SHA256()
    signature = private_key.sign(data, ec.ECDSA(hash))
    return signature
    
def verify(data, signature, public_key):
    hash = hashes.SHA256()
    try:
        public_key.verify(signature, data, ec.ECDSA(hash))
        return True
    except InvalidSignature:
        return False

def toBase64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data)

def fromBase64(data: str) -> bytes:
    return  base64.urlsafe_b64decode(data)
