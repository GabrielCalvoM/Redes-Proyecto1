from interfaz_red_enlace import InterfazRedEnlace


class ConstructorArchivo:
    def __init__(self, interfaz: InterfazRedEnlace):
        self.interfaz = interfaz
        self._datos: bytes | None = None

    def reconstruir(self) -> bytes:
        """
        Bloquea hasta recibir la notificación, luego ensambla y
        retorna los bytes completos del archivo.
        """
        print("[ConstructorArchivo] Esperando paquetes...")
        self.interfaz.wait()

        fragmentos = []
        while (paquete := self.interfaz.dequeue()) is not None:
            fragmentos.append(paquete.payload)

        self._datos = b"".join(fragmentos)
        print(f"[ConstructorArchivo] {len(fragmentos)} paquete(s) ensamblados "
              f"— {len(self._datos)} bytes reconstruidos.")
        return self._datos

    @property
    def datos(self) -> bytes | None:
        """Bytes reconstruidos, o None si aún no se llamó reconstruir()."""
        return self._datos

    def __repr__(self) -> str:
        estado = f"{len(self._datos)} bytes" if self._datos is not None else "sin datos"
        return f"ConstructorArchivo({estado})"
