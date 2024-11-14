from OpenSSL import crypto
import os

def generate_self_signed_cert():
    # Generate key
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # Generate certificate
    cert = crypto.X509()
    cert.get_subject().C = "US"
    cert.get_subject().ST = "State"
    cert.get_subject().L = "City"
    cert.get_subject().O = "GhostSec"
    cert.get_subject().OU = "Development"
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for one year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')

    # Write certificate
    with open(os.path.join('ssl', 'cert.pem'), 'wb') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    # Write private key
    with open(os.path.join('ssl', 'key.pem'), 'wb') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

    print("Generated self-signed SSL certificate and key")

if __name__ == '__main__':
    generate_self_signed_cert()
