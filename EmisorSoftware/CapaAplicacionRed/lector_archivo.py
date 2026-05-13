import os


class LectorArchivo:
    def __init__(self, path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Archivo no encontrado: '{path}'")

        self.path      = path
        self.nombre    = os.path.basename(path)
        self.tamano    = os.path.getsize(path)   # bytes
        self._contenido: bytes | None = None
        
    def leer(self) -> bytes:
        """Lee el archivo y cachea el contenido. Retorna los bytes."""
        if self._contenido is None:
            with open(self.path, "rb") as f:
                self._contenido = f.read()
            print(f"[LectorArchivo] '{self.nombre}' leído — {self.tamano} bytes")
        return self._contenido

    @property
    def contenido(self) -> bytes:
        """Acceso directo al contenido; lee el archivo si aún no se hizo."""
        return self.leer()

    def __repr__(self) -> str:
        return (
            f"LectorArchivo(nombre='{self.nombre}', "
            f"tamano={self.tamano} B, leído={'sí' if self._contenido else 'no'})"
        )


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else __file__
    lector = LectorArchivo(path)
    data   = lector.leer()
    print(f"Primeros 32 bytes: {data[:32]}")
    print(lector)
