import os


VELOCIDADES_BPS = {
    1: 4800,
    2: 9600,
    3: 19200,
}

TAMANOS_PAYLOAD = {
    1: 100,
    2: 400,
    3: 1000,
}

TAMANOS_VENTANA = {
    1: 3,
    2: 4,
    3: 5,
}


def solicitar_path_archivo() -> str:
    """Solicita y valida el path del archivo a transmitir."""
    while True:
        path = input("  Ingrese el path del archivo: ").strip()
        if not path:
            print("  [!] El path no puede estar vacío.")
            continue
        if not os.path.isfile(path):
            print(f"  [!] Archivo no encontrado: '{path}'")
            continue
        return path


def solicitar_velocidad() -> int:
    """Solicita la velocidad de transmisión"""
    print("\n  Velocidad de transmisión (S):")
    for k, v in VELOCIDADES_BPS.items():
        print(f"    [{k}] {v} bps")
    while True:
        opcion = input("  Seleccione una opción [1-3]: ").strip()
        if opcion in ("1", "2", "3"):
            return VELOCIDADES_BPS[int(opcion)]
        print("  [!] Opción inválida. Ingrese 1, 2 o 3.")


def solicitar_payload() -> int:
    """Solicita el tamaño del payload (P)"""
    print("\n  Tamaño de payload (P) por paquete:")
    for k, v in TAMANOS_PAYLOAD.items():
        print(f"    [{k}] {v} B")
    while True:
        opcion = input("  Seleccione una opción [1-3]: ").strip()
        if opcion in ("1", "2", "3"):
            return TAMANOS_PAYLOAD[int(opcion)]
        print("  [!] Opción inválida. Ingrese 1, 2 o 3.")


def solicitar_ventana() -> int:
    """Solicita el tamaño de la ventana"""
    print("\n  Tamaño de ventana (N) - tramas por ráfaga:")
    for k, v in TAMANOS_VENTANA.items():
        print(f"    [{k}] {v} tramas")
    while True:
        opcion = input("  Seleccione una opción [1-3]: ").strip()
        if opcion in ("1", "2", "3"):
            return TAMANOS_VENTANA[int(opcion)]
        print("  [!] Opción inválida. Ingrese 1, 2 o 3.")


def obtener_parametros() -> dict:
    """
    Ejecuta la interfaz de usuario completa y retorna un dict con
    todos los parámetros de transmisión:
        {
            'path':      str   - ruta del archivo,
            'velocidad': int   - bps (4800 / 9600 / 19200),
            'payload':   int   - bytes por paquete (100 / 400 / 1000),
            'ventana':   int   - tramas por ráfaga (3 / 4 / 5),
        }
    """
    print("=" * 50)
    print("   PROTOCOLO DE TRANSMISIÓN DE ARCHIVOS")
    print("   Capa de Red — Interfaz de Usuario")
    print("=" * 50)

    path      = solicitar_path_archivo()
    velocidad = solicitar_velocidad()
    payload   = solicitar_payload()
    ventana   = solicitar_ventana()

    params = {
        "path":      path,
        "velocidad": velocidad,
        "payload":   payload,
        "ventana":   ventana,
    }

    print("\n  --- Parámetros seleccionados ---")
    print(f"  Archivo   : {path}")
    print(f"  Velocidad : {velocidad} bps")
    print(f"  Payload   : {payload} B/paquete")
    print(f"  Ventana   : {ventana} tramas/ráfaga")
    print("=" * 50)

    return params


if __name__ == "__main__":
    params = obtener_parametros()
    print("\n[DEBUG] Parámetros:", params)
