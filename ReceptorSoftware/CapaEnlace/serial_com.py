from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING, Callable

import serial

if TYPE_CHECKING:
    from .admin import AdministradorTramas


class PuertoSerialReceptor:
    def __init__(self, port: str, timeout: float = 10.0) -> None:
        self._port = port
        self._timeout = timeout
        self._ser: serial.Serial | None = None

    def conectar(self) -> None:
        self._ser = serial.Serial(self._port, 9600, timeout=self._timeout)
        sleep(2)
        print(f"[Serial] Escuchando en {self._port} @ 9600 bps")

    def cerrar(self) -> None:
        if self._ser and self._ser.is_open:
            self._ser.close()

    def _leer_trama(self) -> bytes:
        first = self._ser.read(1)
        if not first:
            return b""
        frame_type = first[0] & 0x03
        if frame_type == 0:                         # CONNECTION: 6 bytes total
            rest = self._ser.read(5)
            return (first + rest) if len(rest) == 5 else b""
        if frame_type == 1:                         # DATA
            header = self._ser.read(3)              # seq(1) + size(2)
            if len(header) != 3:
                return b""
            size = int.from_bytes(header[1:3], "big")
            if size > 1000:
                return b""
            tail = self._ser.read(size + 3)         # payload + checksum(2) + trailer(1)
            return (first + header + tail) if len(tail) == size + 3 else b""
        return b""

    def _cambiar_baud(self, baud: int) -> None:
        if self._ser.baudrate != baud:
            self._ser.baudrate = baud
            print(f"[Serial] Velocidad cambiada a {baud} bps")

    def _send_nack(self, admin: AdministradorTramas, seq: int) -> None:
        self._ser.write(admin.build_nack(seq))
        self._ser.reset_input_buffer()
        print(f"[Serial] NACK enviado (seq={seq})")

    def escuchar(
        self,
        admin: AdministradorTramas,
        on_payload: Callable[[bytes], None],
        on_done: Callable[[], None],
    ) -> None:
        # --- Wait for handshake ---
        print("[Serial] Esperando handshake...")
        parsed: dict = {}
        while True:
            frame = self._leer_trama()
            if not frame:
                continue
            try:
                parsed = admin.parse_incoming_frame(frame)
                if parsed["type"] == "connection":
                    break
            except ValueError as exc:
                print(f"[Serial] Trama ignorada: {exc}")

        print(
            f"[Serial] Handshake recibido: "
            f"P={parsed['payload_size']}B  N={parsed['window_size']}  "
            f"S={parsed['speed_bps']}bps  seqs={parsed['sequence_count']}"
        )
        self._ser.write(admin.build_ack(0))
        print("[Serial] ACK de handshake enviado.")

        sleep(0.5)
        self._cambiar_baud(admin.session.speed_bps)

        # --- Sliding-window Go-Back-N receive ---
        expected    = admin.session.sequence_count
        window_size = admin.session.window_size
        total       = 0

        while total < expected:
            frame = self._leer_trama()

            if not frame:
                print(f"[Serial] Timeout esperando seq={total}.")
                self._send_nack(admin, total)
                continue

            try:
                parsed = admin.parse_incoming_frame(frame)
            except ValueError as exc:
                print(f"[Serial] Checksum inválido: {exc}.")
                self._send_nack(admin, total)
                continue

            if parsed["type"] != "data":
                continue

            seq = parsed["sequence"]
            if seq != total:
                print(f"[Serial] Secuencia inesperada: recibida {seq}, esperada {total}.")
                self._send_nack(admin, total)
                continue

            on_payload(parsed["payload"])
            total += 1

            # Send ONE cumulative ACK at the end of each burst or after the last frame.
            is_burst_end = (total % window_size == 0)
            is_last      = (total == expected)
            if is_burst_end or is_last:
                self._ser.write(admin.build_ack(seq))
                print(
                    f"[Serial] ACK enviado (seq={seq}) — "
                    f"{total}/{expected} trama(s) recibidas"
                )

        print("[Serial] Todas las tramas recibidas.")
        on_done()
