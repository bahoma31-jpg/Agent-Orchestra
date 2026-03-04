"""utils.env_encryption

تشفير/فك تشفير ملفات .env باستخدام Fernet (cryptography).

الاستخدام (CLI):
    python -m utils.env_encryption --generate-key
    python -m utils.env_encryption --encrypt .env --out .env.enc
    python -m utils.env_encryption --decrypt .env.enc --out .env

ملاحظات أمنية:
- لا تخزّن المفتاح داخل المستودع.
- اجعل ENV_ENCRYPTION_KEY في متغيرات البيئة أو في مدير أسرار.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class EnvEncryptionError(Exception):
    """خطأ متعلق بتشفير/فك تشفير ملفات البيئة."""


@dataclass(frozen=True)
class EnvCryptoResult:
    """نتيجة عملية التشفير/فك التشفير."""

    input_path: str
    output_path: str
    bytes_in: int
    bytes_out: int


def _require_cryptography():
    try:
        from cryptography.fernet import Fernet  # noqa: F401
    except Exception as exc:  # pragma: no cover
        raise EnvEncryptionError(
            "cryptography غير مثبتة. ثبّت المتطلبات: pip install -r requirements.txt"
        ) from exc


def generate_fernet_key() -> str:
    """إنشاء مفتاح Fernet (Base64 string)."""

    _require_cryptography()
    from cryptography.fernet import Fernet

    return Fernet.generate_key().decode("utf-8")


def encrypt_env_file(
    input_path: str | Path,
    output_path: str | Path,
    key: str,
) -> EnvCryptoResult:
    """تشفير ملف نصي (مثل .env) وكتابة الناتج كـ bytes."""

    _require_cryptography()
    from cryptography.fernet import Fernet

    in_path = Path(input_path)
    out_path = Path(output_path)

    if not in_path.exists():
        raise EnvEncryptionError(f"Input file not found: {in_path}")

    plain = in_path.read_bytes()
    try:
        token = Fernet(key.encode("utf-8")).encrypt(plain)
    except Exception as exc:
        raise EnvEncryptionError("Invalid encryption key") from exc

    out_path.write_bytes(token)

    return EnvCryptoResult(
        input_path=str(in_path),
        output_path=str(out_path),
        bytes_in=len(plain),
        bytes_out=len(token),
    )


def decrypt_env_file(
    input_path: str | Path,
    output_path: str | Path,
    key: str,
) -> EnvCryptoResult:
    """فك تشفير ملف مُشفّر (Fernet token) وكتابة النص الأصلي."""

    _require_cryptography()
    from cryptography.fernet import Fernet, InvalidToken

    in_path = Path(input_path)
    out_path = Path(output_path)

    if not in_path.exists():
        raise EnvEncryptionError(f"Input file not found: {in_path}")

    token = in_path.read_bytes()

    try:
        plain = Fernet(key.encode("utf-8")).decrypt(token)
    except InvalidToken as exc:
        raise EnvEncryptionError("Decryption failed: invalid token or key") from exc
    except Exception as exc:
        raise EnvEncryptionError("Decryption failed") from exc

    out_path.write_bytes(plain)

    return EnvCryptoResult(
        input_path=str(in_path),
        output_path=str(out_path),
        bytes_in=len(token),
        bytes_out=len(plain),
    )


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Encrypt/decrypt .env files using Fernet")

    p.add_argument("--generate-key", action="store_true", help="Generate a Fernet key")
    p.add_argument("--encrypt", type=str, default=None, help="Encrypt input file path")
    p.add_argument("--decrypt", type=str, default=None, help="Decrypt input file path")
    p.add_argument("--out", type=str, default=None, help="Output file path")
    p.add_argument("--key", type=str, default=None, help="Fernet key (Base64)")

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.generate_key:
        print(generate_fernet_key())
        return 0

    if bool(args.encrypt) == bool(args.decrypt):
        parser.error("Choose exactly one of --encrypt or --decrypt")

    if not args.out:
        parser.error("--out is required")

    if not args.key:
        parser.error("--key is required")

    if args.encrypt:
        encrypt_env_file(args.encrypt, args.out, args.key)
        return 0

    decrypt_env_file(args.decrypt, args.out, args.key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
