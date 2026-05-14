import threading
from collections import deque
from typing import Optional

from paquete import Paquete


class InterfazRedEnlace:
    def __init__(self):
        self._queue: deque[Paquete] = deque()
        self._evento = threading.Event()

    def enqueue(self, paquete: Paquete) -> None:
        self._queue.append(paquete)

    def dequeue(self) -> Optional[Paquete]:
        return self._queue.popleft() if self._queue else None

    def __len__(self) -> int:
        return len(self._queue)

    def notificar_fin_recepcion(self) -> None:
        """
        La capa de enlace llama esto al entregar la última trama.
        Avisa al constructor de archivo que ya estan listos todos los paquetes
        """
        self._evento.set()

    def wait(self) -> None:
        """El constructor de archivo llama esto para bloquearse hasta notificar_fin_recepcion()."""
        self._evento.wait()

    def __repr__(self) -> str:
        listo = self._evento.is_set()
        return f"InterfazCapasReceptor(pendientes={len(self._queue)}, listo={listo})"
