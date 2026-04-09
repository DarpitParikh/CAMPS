#!/usr/bin/env python
from py_vapid import Vapid01
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

v = Vapid01.from_file('private_key.pem')

# Get public key bytes in uncompressed format (65 bytes for P-256)
pub_bytes = v.public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

# For EC private keys, extract the raw d value (32 bytes for P-256)
priv_obj = v.private_key
priv_numbers = priv_obj.private_numbers()
# Convert private value to 32-byte format (big-endian)
priv_bytes = priv_numbers.private_value.to_bytes(32, byteorder='big')

# Encode to base64url (without padding)
pub_b64 = base64.urlsafe_b64encode(pub_bytes).decode().rstrip('=')
priv_b64 = base64.urlsafe_b64encode(priv_bytes).decode().rstrip('=')

print(f"WEBPUSH_PUBLIC_KEY={pub_b64}")
print(f"WEBPUSH_PRIVATE_KEY={priv_b64}")
