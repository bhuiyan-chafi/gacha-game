from OpenSSL import crypto


def create_self_signed_cert(cert_file, key_file):
    # Generate a key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # Create a self-signed certificate
    cert = crypto.X509()
    cert.get_subject().C = "IT"
    cert.get_subject().ST = "Toscano"
    cert.get_subject().L = "Pisa"
    cert.get_subject().O = "UiPi"
    cert.get_subject().OU = "CJMS"
    cert.get_subject().CN = "localhost"
    cert.get_subject().emailAddress = "cjms@unipi.com"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # 1 year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, "sha256")

    # Write the private key and certificate to files
    with open(cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    print(f"Certificate and key generated: {cert_file}, {key_file}")


if __name__ == "__main__":
    create_self_signed_cert("cert.pem", "key.pem")
