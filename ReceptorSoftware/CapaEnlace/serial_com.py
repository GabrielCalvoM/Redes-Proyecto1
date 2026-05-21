from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING, Callable

import serial

if TYPE_CHECKING:
    from .admin import AdministradorTramas


class PuertoSerialReceptor:
    def __init__(self, port: str, timeout: float = 5.0) -> None:
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
        if frame_type == 0:  # CONNECTION: 6 bytes total
            rest = self._ser.read(5)
            return (first + rest) if len(rest) == 5 else b""
        if frame_type == 1:  # DATA: header(4) + payload + checksum(2) + trailer(1)
            header = self._ser.read(3)  # seq(1) + size(2)
            if len(header) != 3:
                return b""
            size = int.from_bytes(header[1:3], "big")
            tail = self._ser.read(size + 3)  # payload + checksum(2) + trailer(1)
            return (first + header + tail) if len(tail) == size + 3 else b""
        return b""

    def _cambiar_baud(self, baud: int) -> None:
        if self._ser.baudrate != baud:
            self._ser.baudrate = baud
            print(f"[Serial] Velocidad cambiada a {baud} bps")

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

        # Acknowledge the handshake
        ack = admin.build_ack(0)
        self._ser.write(ack)
        print("[Serial] ACK de handshake enviado.")

        # Give the Arduino time to reinitialize its serial port.
        sleep(0.5)
        self._cambiar_baud(admin.session.speed_bps)

        # --- Receive data frames ---
        expected = admin.session.sequence_count
        received = 0

        while received < expected:
            frame = self._leer_trama()
            if not frame:
                print(
                    f"[Serial] Timeout esperando trama {received + 1}/{expected}. "
                    f"Enviando NACK (seq={received})..."
                )
                self._ser.write(admin.build_nack(received))
                continue

            try:
                parsed = admin.parse_incoming_frame(frame)
            except ValueError as exc:
                print(f"[Serial] Checksum inválido: {exc}. Enviando NACK (seq={received})...")
                self._ser.write(admin.build_nack(received))
                continue

            if parsed["type"] != "data":
                continue

            on_payload(parsed["payload"])
            received += 1
            self._ser.write(admin.build_ack(parsed["sequence"]))
            print(
                f"[Serial] Trama {received}/{expected} ok "
                f"(seq={parsed['sequence']}, {parsed['size']}B)"
            )

        print("[Serial] Todas las tramas recibidas.")
        on_done()
