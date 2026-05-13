from collections import deque
from typing import Optional

from paquetizador import Paquete


class InterfazRedEnlace:
    """
    Queue FIFO de paquetes entre capas.
    """

    def __init__(self):
        self._queue: deque[Paquete] = deque()

    def enqueue(self, paquete: Paquete) -> None:
        self._queue.append(paquete)

    def dequeue(self) -> Optional[Paquete]:
        return self._queue.popleft() if self._queue else None

    def __len__(self) -> int:
        return len(self._queue)

    def __repr__(self) -> str:
        return f"InterfazCapas(pendientes={len(self._queue)})"