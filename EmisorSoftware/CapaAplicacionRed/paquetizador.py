import math
from dataclasses import dataclass

from lector_archivo import LectorArchivo


@dataclass
class Paquete:
    payload: bytes

    def __repr__(self) -> str:
        return f"Paquete(bytes={len(self.payload)})"


class Paquetizador:
    def __init__(self, lector: LectorArchivo, tamano_payload: int):
        if tamano_payload <= 0:
            raise ValueError("El tamaño de payload debe ser > 0")

        self.lector          = lector
        self.tamano_payload  = tamano_payload   # P
        self._total_paquetes: int | None = None

    def calcular_total(self) -> int:
        """Retorna el número total de paquetes necesarios para el archivo."""
        if self._total_paquetes is None:
            self._total_paquetes = math.ceil(
                self.lector.tamano / self.tamano_payload
            )
        return self._total_paquetes

    def segmentar(self):
        """
        Generador: produce cada Paquete en orden de secuencia.
        Lee el archivo si aún no está en memoria.
        """
        contenido = self.lector.contenido
        total     = self.calcular_total()
        P         = self.tamano_payload

        print(
            f"[Paquetizador] Segmentando '{self.lector.nombre}' en "
            f"{total} paquete(s) de {P} B"
        )

        for i in range(total):
            inicio = i * P
            bloque = contenido[inicio:inicio + P]
            yield Paquete(payload=bloque)

    def empaquetar_y_enviar(self, interfaz) -> int:
        """
        Itera sobre todos los paquetes y los encola en `interfaz`
        (InterfazRedEnlace). Retorna la cantidad de paquetes enviados.
        """
        enviados = 0
        for paquete in self.segmentar():
            interfaz.enqueue(paquete)
            enviados += 1
            print(f"  → Encolado: {paquete}")

        print(f"[Paquetizador] {enviados} paquete(s) escritos al buffer.")
        return enviados

    def __repr__(self) -> str:
        return (
            f"Paquetizador(archivo='{self.lector.nombre}', "
            f"P={self.tamano_payload} B, "
            f"total={self.calcular_total()} paquetes)"
        )


if __name__ == "__main__":

    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else __file__
    P    = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    lector = LectorArchivo(path)
    paq    = Paquetizador(lector, P)
    print(paq)
    for p in paq.segmentar():
        print(p)