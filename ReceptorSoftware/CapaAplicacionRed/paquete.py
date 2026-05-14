from dataclasses import dataclass


@dataclass
class Paquete:
    payload: bytes

    def __repr__(self) -> str:
        return f"Paquete(bytes={len(self.payload)})"
