import os
import sys

from interfaz_red_enlace import InterfazRedEnlace
from constructor_archivo import ConstructorArchivo
from interfaz_usuario import (
    mostrar_escuchando,
    mostrar_archivo_recibido,
    solicitar_destino,
    guardar_archivo,
)
from paquete import Paquete


BASE_DIR = os.path.dirname(__file__)
RECEPTOR_DIR = os.path.dirname(BASE_DIR)
if RECEPTOR_DIR not in sys.path:
    sys.path.insert(0, RECEPTOR_DIR)

from CapaEnlace.admin      import AdministradorTramas
from CapaEnlace.serial_com import PuertoSerialReceptor


def main():
    puerto_serial = sys.argv[1] if len(sys.argv) > 1 else "COM4"

    interfaz = InterfazRedEnlace()
    admin = AdministradorTramas()

    mostrar_escuchando()
    print(f"  Puerto serial : {puerto_serial}")

    # --- Capa Física / Enlace: recibe tramas y puebla la interfaz ---
    puerto = PuertoSerialReceptor(puerto_serial)
    puerto.conectar()
    try:
        puerto.escuchar(
            admin,
            on_payload=lambda payload: interfaz.enqueue(Paquete(payload=payload)),
            on_done=interfaz.notificar_fin_recepcion,
        )
    finally:
        puerto.cerrar()

    # --- Capa de Red / Aplicación: reconstruye el archivo ---
    constructor = ConstructorArchivo(interfaz)
    datos = constructor.reconstruir()

    mostrar_archivo_recibido(len(datos))
    directorio, nombre = solicitar_destino()
    guardar_archivo(datos, directorio, nombre)


if __name__ == "__main__":
    main()
