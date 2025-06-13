import hashlib
import subprocess

SECRET_KEY = "mi_clave_secreta"  # Debe coincidir con la usada en generador_licencia.py


def obtener_serial() -> str:
    """Devuelve el serial del primer disco usando wmic (solo en Windows)."""
    try:
        salida = subprocess.check_output(
            ["wmic", "diskdrive", "get", "SerialNumber"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        lineas = [l.strip() for l in salida.splitlines() if l.strip()]
        return lineas[1] if len(lineas) > 1 else ""
    except Exception:
        return ""


def calcular_clave(serial: str) -> str:
    datos = (serial + SECRET_KEY).encode()
    return hashlib.sha256(datos).hexdigest()


def main():
    serial = obtener_serial()
    if not serial:
        print("No se pudo obtener el serial del disco.")
        return
    print(f"ID de hardware: {serial}")
    clave_ingresada = input("Ingrese la clave de activacion: ").strip()
    clave_correcta = calcular_clave(serial)
    if clave_ingresada == clave_correcta:
        print("Programa activado correctamente!")
    else:
        print("Clave invalida. Por favor verifique el serial y la clave.")


if __name__ == "__main__":
    main()
