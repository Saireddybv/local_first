"""Generate a local CA and server certificate; never installs a trust root."""
import argparse
import ipaddress
from datetime import datetime, timedelta, timezone
from pathlib import Path


def generate(address, output):
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

    address = ipaddress.ip_address(address)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    names = ["ca.pem", "ca-key.pem", "server.pem", "server-key.pem"]
    if any((output / name).exists() for name in names):
        raise ValueError("Certificate files already exist. Use another output folder to avoid replacing trusted keys.")
    now = datetime.now(timezone.utc)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Local First Personal CA")])
    ca = (x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name)
          .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=365))
          .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
          .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False,
                                      key_encipherment=False, data_encipherment=False, key_agreement=False,
                                      key_cert_sign=True, crl_sign=True, encipher_only=False, decipher_only=False), critical=True)
          .sign(ca_key, hashes.SHA256()))
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server = (x509.CertificateBuilder()
              .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Local First")]))
              .issuer_name(ca_name).public_key(server_key.public_key()).serial_number(x509.random_serial_number())
              .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=90))
              .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
              .add_extension(x509.SubjectAlternativeName([x509.IPAddress(address), x509.IPAddress(ipaddress.ip_address("127.0.0.1")), x509.DNSName("localhost")]), critical=False)
              .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
              .sign(ca_key, hashes.SHA256()))
    for filename, key in [("ca-key.pem", ca_key), ("server-key.pem", server_key)]:
        (output / filename).write_bytes(key.private_bytes(serialization.Encoding.PEM,
                                                        serialization.PrivateFormat.PKCS8,
                                                        serialization.NoEncryption()))
    (output / "ca.pem").write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    (output / "server.pem").write_bytes(server.public_bytes(serialization.Encoding.PEM))
    (output / "Local-First-CA.cer").write_bytes(ca.public_bytes(serialization.Encoding.DER))
    return output


def main():
    parser = argparse.ArgumentParser(description="Create Local First TLS certificates without changing device trust settings")
    parser.add_argument("--address", required=True, help="Laptop's current LAN IP address")
    parser.add_argument("--out", default=".certs", help="Private output folder, outside the shared files folder")
    args = parser.parse_args()
    try:
        output = generate(args.address, args.out)
    except (ValueError, ImportError) as exc:
        parser.error(str(exc))
    print(f"Certificates created in {output.resolve()}")
    print("Trust only Local-First-CA.cer on your own devices. Never share either private key.")
    print("See docs/https.md for device trust and startup instructions.")


if __name__ == "__main__":
    main()
