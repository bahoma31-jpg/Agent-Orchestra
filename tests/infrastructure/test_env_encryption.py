"""tests.infrastructure.test_env_encryption

اختبار أن نظام تشفير .env يعمل كما هو مطلوب في المرحلة 1.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from utils.env_encryption import (
    EnvEncryptionError,
    decrypt_env_file,
    encrypt_env_file,
    generate_fernet_key,
)


def test_env_encryption_works(tmp_path: Path) -> None:
    key = generate_fernet_key()

    env_plain = tmp_path / ".env"
    env_plain.write_text("HELLO=world\nSECRET=123\n", encoding="utf-8")

    encrypted = tmp_path / ".env.enc"
    decrypted = tmp_path / ".env.dec"

    encrypt_result = encrypt_env_file(env_plain, encrypted, key)
    assert encrypt_result.bytes_in > 0
    assert encrypted.exists()

    encrypted_bytes = encrypted.read_bytes()
    assert b"SECRET=123" not in encrypted_bytes

    decrypt_result = decrypt_env_file(encrypted, decrypted, key)
    assert decrypt_result.bytes_out > 0

    assert decrypted.read_text(encoding="utf-8") == env_plain.read_text(encoding="utf-8")


def test_env_encryption_wrong_key_fails(tmp_path: Path) -> None:
    key = generate_fernet_key()
    wrong_key = generate_fernet_key()

    env_plain = tmp_path / ".env"
    env_plain.write_text("A=1\n", encoding="utf-8")

    encrypted = tmp_path / ".env.enc"
    decrypted = tmp_path / ".env.dec"

    encrypt_env_file(env_plain, encrypted, key)

    with pytest.raises(EnvEncryptionError):
        decrypt_env_file(encrypted, decrypted, wrong_key)
