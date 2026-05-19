import os
import sys

from interfaz_usuario import obtener_parametros
from lector_archivo   import LectorArchivo
from paquetizador     import Paquetizador
from interfaz_red_enlace   import InterfazRedEnlace


BASE_DIR = os.path.dirname(__file__)
EMISOR_DIR = os.path.dirname(BASE_DIR)
if EMISOR_DIR not in sys.path:
    sys.path.insert(0, EMISOR_DIR)

from CapaEnlace.admin import AdministradorTramas


def main():
    # Interfaz de Usuario: recolectar parámetros
    params = obtener_parametros()

    # Lector: abrir y leer el archivo
    lector = LectorArchivo(params["path"])
    lector.leer()

    # Interfaz Red-Enlace (con el buffer de paquetes)
    interfaz = InterfazRedEnlace()

    # Paquetizador: crear paquetes y escribir al buffer
    paquetizador = Paquetizador(lector, params["payload"])
    print(f"\n[main] {paquetizador}")
    paquetizador.empaquetar_y_enviar(interfaz)


    print("\n" + "=" * 50)
    print(" Capa de Red")
    print("=" * 50)
    print(f"  Archivo         : {lector.nombre}")
    print(f"  Tamaño          : {lector.tamano} bytes")
    print(f"  Velocidad (S)   : {params['velocidad']} bps")
    print(f"  Payload (P)     : {params['payload']} B/paquete")
    print(f"  Ventana (N)     : {params['ventana']} tramas/ráfaga")
    print(f"  Hamming   : {'Sí' if params['hamming'] else 'No'}")
    print(f"  Total paquetes  : {paquetizador.calcular_total()}")
    print(f"  Paquetes en cola: {len(interfaz)}")
    print("=" * 50)

    administrador = AdministradorTramas()
    administrador.configure_session(
        payload_size=params["payload"],
        window_size=params["ventana"],
        speed_bps=params["velocidad"],
        hamming_enabled=params["hamming"],
    )
    administrador.load_transfer_from_interface(interfaz)

    print("\n[main] Tramas construidas por el administrador:")
    while administrador.has_pending_frames() or administrador.has_pending_bursts():
        while administrador.has_pending_frames():
            frame = administrador.next_frame()
            if frame is not None:
                print(f"  {frame}")
        if administrador.has_pending_bursts():
            administrador.load_next_burst()


if __name__ == "__main__":
    main()