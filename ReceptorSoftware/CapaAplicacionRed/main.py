from interfaz_red_enlace import InterfazRedEnlace
from constructor_archivo import ConstructorArchivo
from interfaz_usuario  import (
    mostrar_escuchando,
    mostrar_archivo_recibido,
    solicitar_destino,
    guardar_archivo,
)


def main():
    # 1. Crear la interfaz entre capas (la capa de enlace la recibe por referencia)
    interfaz = InterfazRedEnlace()

    # 2. Avisar al usuario que estamos escuchando
    mostrar_escuchando()

    # 3. Constructor: bloquea hasta que la capa de enlace llame notificar_fin_recepcion()
    constructor = ConstructorArchivo(interfaz)
    datos = constructor.reconstruir()

    # 4. Notificar al usuario que el archivo llegó
    mostrar_archivo_recibido(len(datos))

    # 5. Preguntar destino y guardar
    directorio, nombre = solicitar_destino()
    guardar_archivo(datos, directorio, nombre)

    return interfaz   # la capa de enlace ya tiene su referencia; esto es opcional


if __name__ == "__main__":
    # ── Demo sin capa de enlace real ──────────────────────────────────
    # Simula la capa inferior encolando paquetes y llamando notificar_fin_recepcion().
    import threading
    from paquete import Paquete

    interfaz = InterfazRedEnlace()

    def simular_capa_enlace():
        import time
        time.sleep(1)   # simula latencia de red
        contenido = (
            b"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla luctus lacus metus,\n"
            b"in faucibus nulla viverra vitae. Nam ex magna, consequat sed justo ac, accumsan\n"
            b"blandit ipsum. Duis vulputate ante nec rhoncus condimentum. Pellentesque vulputate\n"
            b"vitae sapien sed dictum. Ut non ante bibendum, iaculis orci quis, pellentesque quam.\n"
        )
        P = 20
        for i in range(0, len(contenido), P):
            interfaz.enqueue(Paquete(payload=contenido[i:i+P]))
        print("[SimuladorEnlace] Paquetes encolados. Notificando...")
        interfaz.notificar_fin_recepcion()

    hilo = threading.Thread(target=simular_capa_enlace, daemon=True)
    hilo.start()

    # Capa de aplicación
    mostrar_escuchando()
    constructor = ConstructorArchivo(interfaz)
    datos = constructor.reconstruir()
    mostrar_archivo_recibido(len(datos))
    directorio, nombre = solicitar_destino()
    guardar_archivo(datos, directorio, nombre)
