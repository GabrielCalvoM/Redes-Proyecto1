import os


def mostrar_escuchando() -> None:
    """Informa al usuario que el sistema está en espera de una transmisión."""
    print("\n" + "=" * 50)
    print("   RECEPTOR — Capa de Aplicación")
    print("=" * 50)
    print("  [*] Escuchando... esperando archivo entrante.")
    print("=" * 50)


def mostrar_archivo_recibido(tamano: int) -> None:
    """Informa al usuario que el archivo fue recibido completamente."""
    print(f"\n  [✓] Archivo recibido — {tamano} bytes reconstruidos.")


def solicitar_destino() -> tuple[str, str]:
    """
    Pregunta al usuario dónde y con qué nombre guardar el archivo.

    Retorna:
        (directorio, nombre_archivo)
    """
    print()

    # Directorio de destino
    while True:
        directorio = input("  Directorio de destino (Enter = directorio actual): ").strip()
        if not directorio:
            directorio = os.getcwd()
        if os.path.isdir(directorio):
            break
        # Ofrecer crear el directorio si no existe
        crear = input(f"  [!] '{directorio}' no existe. ¿Crearlo? [s/n]: ").strip().lower()
        if crear == "s":
            os.makedirs(directorio, exist_ok=True)
            break

    # Nombre del archivo
    while True:
        nombre = input("  Nombre del archivo a guardar: ").strip()
        if nombre:
            break
        print("  [!] El nombre no puede estar vacío.")

    return directorio, nombre


def guardar_archivo(datos: bytes, directorio: str, nombre: str) -> str:
    """
    Escribe los bytes en disco.

    Retorna:
        La ruta completa del archivo guardado.
    """
    ruta = os.path.join(directorio, nombre)

    # Advertir si el archivo ya existe
    if os.path.exists(ruta):
        sobrescribir = input(f"  [!] '{ruta}' ya existe. ¿Sobrescribir? [s/n]: ").strip().lower()
        if sobrescribir != "s":
            print("  [!] Guardado cancelado.")
            return ""

    with open(ruta, "wb") as f:
        f.write(datos)

    print(f"  [✓] Archivo guardado en: {ruta}")
    return ruta
