import base64
import hashlib
import json

from cryptography.fernet import Fernet


def create_key(keypath: str) -> None:
    """
    Generate a new Fernet key and save it to a file.

    Parameters
    ----------
    keypath : str
        Path where the key file will be written.
    """
    # Generate a key
    key = Fernet.generate_key()

    # Save the key securely
    with open(keypath, 'wb') as f:
        f.write(key)


def load_key(keypath: str) -> bytes:
    """
    Load a Fernet key from a file.

    Parameters
    ----------
    keypath : str
        Path to the key file.

    Returns
    -------
    bytes
        The loaded key.
    """
    # Load key from file
    with open(keypath, 'rb') as f:
        key = f.read()
    return key


def encrypt_txt(key: bytes, txt: str | bytes) -> bytes:
    """
    Encrypt a text string with a Fernet key.

    Parameters
    ----------
    key : bytes
        Fernet key (32 url-safe base64-encoded bytes).
    txt : str or bytes
        Text to encrypt.

    Returns
    -------
    bytes
        The encrypted token.
    """
    # Serialize and encrypt the txt
    cipher = Fernet(key)
    encrypted_credentials = cipher.encrypt(
        txt if isinstance(txt, bytes) else txt.encode()
    )
    return encrypted_credentials


def decrypt_txt(key: bytes, txt: bytes) -> bytes:
    """
    Decrypt a Fernet token.

    Parameters
    ----------
    key : bytes
        Fernet key (32 url-safe base64-encoded bytes).
    txt : bytes
        Token to decrypt.

    Returns
    -------
    bytes
        The decrypted payload.

    Raises
    ------
    InvalidToken
        If the key does not match the token.
    """
    # Decrypt the credentials
    cipher = Fernet(key)
    decrypted_credentials = cipher.decrypt(txt)
    return decrypted_credentials


def encrypt_file(key: bytes, filepath: str) -> str:
    """
    Encrypt a file in place, writing the ciphertext to ``<name>_.<ext>``.

    Parameters
    ----------
    key : bytes
        Fernet key (32 url-safe base64-encoded bytes).
    filepath : str
        Path to the file to encrypt.

    Returns
    -------
    str
        Path of the encrypted file.
    """
    # Load the credentials
    with open(filepath, 'rb') as f:
        txt = f.read()
    # Serialize and encrypt the txt
    encrypted_credentials = encrypt_txt(key, txt)
    # Save the encrypted file
    file, ext = filepath.rsplit('.', 1)
    filepath = f'{file}_.{ext}'
    with open(filepath, 'wb') as f:
        f.write(encrypted_credentials)
    return filepath


def decrypt_file(key: bytes, filepath: str, to_json: bool = True) -> str | dict:
    """
    Decrypt a Fernet-encrypted file.

    Parameters
    ----------
    key : bytes
        Fernet key (32 url-safe base64-encoded bytes).
    filepath : str
        Path to the encrypted file.
    to_json : bool, optional
        Parse the decrypted payload as JSON (default is True).

    Returns
    -------
    str or dict
        The decrypted payload, parsed as JSON when ``to_json`` is True.
    """
    # Load the credentials
    with open(filepath, 'rb') as f:
        txt = f.read()
    # Decrypt the credentials
    decrypted_credentials = decrypt_txt(key, txt).decode()
    # Load the credentials into a dictionary
    if to_json:
        decrypted_credentials = json.loads(decrypted_credentials)
    return decrypted_credentials


def ha64(txt: str) -> bytes:
    """
    Hash a string with SHA-256 and base64-url-encode the digest.

    The output is suitable for use as a Fernet key (32 url-safe base64 bytes).

    Parameters
    ----------
    txt : str
        String to hash.

    Returns
    -------
    bytes
        The base64-url-encoded SHA-256 digest.
    """
    txt = hashlib.sha256(txt.encode()).digest()
    return base64.urlsafe_b64encode(txt)
