import json

import pytest
from cryptography.fernet import Fernet, InvalidToken

from mspu.security import (
    create_key,
    decrypt_file,
    decrypt_txt,
    encrypt_file,
    encrypt_txt,
    ha64,
    load_key,
)


def test_create_and_load_key(tmp_path):
    keypath = tmp_path / 'key.key'
    create_key(str(keypath))
    key = load_key(str(keypath))
    assert isinstance(key, bytes)
    assert len(key) == 44  # base64-encoded 32-byte Fernet key


def test_encrypt_decrypt_txt():
    key = Fernet.generate_key()
    token = encrypt_txt(key, 'secret message')
    assert token != b'secret message'
    assert decrypt_txt(key, token) == b'secret message'


def test_encrypt_decrypt_txt_bytes():
    key = Fernet.generate_key()
    token = encrypt_txt(key, b'secret bytes')
    assert decrypt_txt(key, token) == b'secret bytes'


def test_decrypt_wrong_key():
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    token = encrypt_txt(key1, 'secret')
    with pytest.raises(InvalidToken):
        decrypt_txt(key2, token)


def test_encrypt_decrypt_file(tmp_path):
    key = Fernet.generate_key()
    src = tmp_path / 'creds.json'
    src.write_text(json.dumps({'user': 'admin', 'pass': 'hunter2'}))

    encrypted_path = encrypt_file(key, str(src))
    assert encrypted_path == str(tmp_path / 'creds_.json')
    assert tmp_path / 'creds_.json' in tmp_path.iterdir()

    decrypted = decrypt_file(key, encrypted_path)
    assert decrypted == {'user': 'admin', 'pass': 'hunter2'}


def test_decrypt_file_plain(tmp_path):
    key = Fernet.generate_key()
    src = tmp_path / 'note.txt'
    src.write_text('plain text')
    encrypted_path = encrypt_file(key, str(src))
    decrypted = decrypt_file(key, encrypted_path, to_json=False)
    assert decrypted == 'plain text'


def test_ha64_returns_fernet_compatible_key():
    key = ha64('my-secret')
    assert len(key) == 44
    # must be usable as a Fernet key
    token = encrypt_txt(key, 'works')
    assert decrypt_txt(key, token) == b'works'


def test_ha64_deterministic():
    assert ha64('same-input') == ha64('same-input')
    assert ha64('same-input') != ha64('different')
