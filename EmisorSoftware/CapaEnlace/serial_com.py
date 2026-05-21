from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

import serial

if TYPE_CHECKING:
    from .admin import AdministradorTramas


class PuertoSerialEmisor:
    def __init__(self, port: str, timeout: float = 5.0) -> None:
        self._port = port
        self._timeout = timeout
        self._ser: serial.Serial | None = None

    def conectar(self) -> None:
        self._ser = serial.Serial(self._port, 9600, timeout=self._timeout)
        sleep(2)
        print(f"[Serial] Conectado a {self._port} @ 9600 bps")

    def cerrar(self) -> None:
        if self._ser and self._ser.is_open:
            self._ser.close()

    def _leer_respuesta(self) -> bytes | None:
        raw = self._ser.read(5)
        return raw if len(raw) == 5 else None

    def _cambiar_baud(self, baud: int) -> None:
        if self._ser.baudrate != baud:
            self._ser.baudrate = baud
            print(f"[Serial] Velocidad cambiada a {baud} bps")

    def enviar_transferencia(
        self,
        admin: AdministradorTramas,
        connection_frame: bytes,
        bursts: list[list[bytes]],
    ) -> None:
        # --- Handshake ---
        print(f"[Serial] Enviando handshake ({len(connection_frame)} bytes)...")
        self._ser.write(connection_frame)

        raw = self._leer_respuesta()
        if raw is None:
            raise TimeoutError("No se recibió ACK tras el handshake")
        try:
            resp = admin.parse_control_frame(raw)
        except ValueError as exc:
            raise RuntimeError(f"Respuesta inválida al handshake: {exc}") from exc

        if resp["type"] != "ack":
            raise RuntimeError(f"Se esperaba ACK, se recibió: {resp['type']}")
        print(f"[Serial] Handshake confirmado (seq={resp['sequence']}). Iniciando transferencia...")

        # Give the Arduino time to reinitialize its serial port to the session speed.
        sleep(0.5)
        self._cambiar_baud(admin.session.speed_bps)

        # --- Data frames (one at a time, one ACK per frame) ---
        total_bursts = len(bursts)
        for i, burst in enumerate(bursts):
            print(f"[Serial] Ráfaga {i + 1}/{total_bursts} ({len(burst)} trama(s))")
            for frame in burst:
                while True:
                    self._ser.write(frame)
                    raw = self._leer_respuesta()
                    if raw is None:
                        print("[Serial] Timeout. Retransmitiendo trama...")
                        continue
                    try:
                        resp = admin.parse_control_frame(raw)
                    except ValueError as exc:
                        print(f"[Serial] Respuesta inválida: {exc}. Retransmitiendo...")
                        continue
                    if resp["type"] == "ack":
                        break
                    print(f"[Serial] NACK (seq={resp['sequence']}). Retransmitiendo...")

        print("[Serial] Transferencia completada.")
