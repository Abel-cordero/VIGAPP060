import hashlib
import sys

SECRET_KEY = "mi_clave_sercreta"  # Cambiar por la clave real


def generar_clave(serial: str) -> str:
    """Genera el hash SHA256 de serial+SECRET_KEY."""
    data = (serial + SECRET_KEY).encode()
    return hashlib.sha256(data).hexdigest()


def main():
    if len(sys.argv) != 2:
        print("Uso: python generador_licencia.py <serial>")
        sys.exit(1)
    serial = sys.argv[1]
    clave = generar_clave(serial)
    print(clave)


if __name__ == "__main__":
    main()
