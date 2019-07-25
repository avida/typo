import crypto_utils
import cryptography
import random

def getRandomBytes(length):
    return bytes(map(lambda _: random.randint(0, 255), range(length)))

def test_generate_key():
    key = crypto_utils.generateECKey()
    assert type(key) == cryptography.hazmat.backends.openssl.ec._EllipticCurvePrivateKey

def test_serialize_key():
    key = crypto_utils.generateECKey()
    key_data = crypto_utils.serializeECKey(key)
    assert type(key_data) == bytes
    assert len(key_data) != 0
    loaded_key = crypto_utils.loadECKey(key_data)
    loaded_key_data = crypto_utils.serializeECKey(loaded_key)
    assert key_data == loaded_key_data
# Check if public key is matching and serializing correctlu
    public_key_data = crypto_utils.serializePublicKey(key.public_key())
    assert type(public_key_data) == bytes
    assert len(public_key_data) != 0
    public_key2_data = crypto_utils.serializePublicKey(loaded_key.public_key())
    assert type(public_key2_data) == bytes
    assert len(public_key2_data) != 0
    assert public_key_data == public_key2_data

def test_base64():
    key = crypto_utils.generateECKey()
    key_data = crypto_utils.serializeECKey(key)
    dec = crypto_utils.toBase64(key_data)
    assert len(dec) != 0
    undec = crypto_utils.fromBase64(dec)
    assert len(undec) != 0
    assert undec == key_data
    some_key = crypto_utils.fromBase64("_____")
    assert some_key == None

def test_sign_data():
    key = crypto_utils.generateECKey()
    public_key = key.public_key()
    data_to_sign = getRandomBytes(50)
    signature = crypto_utils.sign(data_to_sign, key)
    assert type(signature) == bytes
    assert len(signature) != 0
    for _ in range(5):
        assert crypto_utils.verify(data_to_sign, signature, public_key)
    random_data = getRandomBytes(50)
    for _ in range(5):
        assert not crypto_utils.verify(random_data, signature, public_key)
    for _ in range(5):
        assert crypto_utils.verify(data_to_sign, signature, public_key)

def test_load_bad_key():
    key = crypto_utils.generateECKey()
    key_data = crypto_utils.serializeECKey(key)
    public_key_data = crypto_utils.serializePublicKey(key.public_key())
    random_data = getRandomBytes(len(key_data))
    bad_key = crypto_utils.loadECKey(random_data)
    assert bad_key == None
    random_data = getRandomBytes(len(public_key_data))
    bad_key = crypto_utils.loadPublicKey(None)
    assert bad_key == None
    bad_key = crypto_utils.loadPublicKey(random_data)
    assert bad_key == None
