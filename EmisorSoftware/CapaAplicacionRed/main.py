import os
import sys

from interfaz_usuario import obtener_parametros
from lector_archivo   import LectorArchivo
from paquetizador     import Paquetizador
from interfaz_red_enlace import InterfazRedEnlace


BASE_DIR = os.path.dirname(__file__)
EMISOR_DIR = os.path.dirname(BASE_DIR)
if EMISOR_DIR not in sys.path:
    sys.path.insert(0, EMISOR_DIR)

from CapaEnlace.admin      import AdministradorTramas
from CapaEnlace.serial_com import PuertoSerialEmisor


def main():
    puerto_serial = sys.argv[1] if len(sys.argv) > 1 else "COM7"

    # --- Capa de Aplicación / Red ---
    params = obtener_parametros()

    lector = LectorArchivo(params["path"])
    lector.leer()

    interfaz = InterfazRedEnlace()
    paquetizador = Paquetizador(lector, params["payload"])
    paquetizador.empaquetar_y_enviar(interfaz)

    print("\n" + "=" * 50)
    print(" Capa de Red — Resumen")
    print("=" * 50)
    print(f"  Archivo       : {lector.nombre}")
    print(f"  Tamaño        : {lector.tamano} bytes")
    print(f"  Velocidad (S) : {params['velocidad']} bps")
    print(f"  Payload (P)   : {params['payload']} B/paquete")
    print(f"  Ventana (N)   : {params['ventana']} tramas/ráfaga")
    print(f"  Hamming       : {'Sí' if params['hamming'] else 'No'}")
    print(f"  Paquetes      : {paquetizador.calcular_total()}")
    print("=" * 50)

    # --- Capa de Enlace ---
    administrador = AdministradorTramas()
    administrador.configure_session(
        payload_size=params["payload"],
        window_size=params["ventana"],
        speed_bps=params["velocidad"],
        hamming_enabled=params["hamming"],
    )

    # Drain queue and build frames
    packets = []
    while len(interfaz) > 0:
        packets.append(interfaz.dequeue())
    connection_frame, data_frames = administrador.prepare_bursts_from_packets(packets)

    # --- Capa Física (serial hacia Arduino) ---
    puerto = PuertoSerialEmisor(puerto_serial, timeout=120.0)
    try:
        puerto.conectar()
        puerto.enviar_transferencia(administrador, connection_frame, data_frames)
    finally:
        puerto.cerrar()


if __name__ == "__main__":
    main()
