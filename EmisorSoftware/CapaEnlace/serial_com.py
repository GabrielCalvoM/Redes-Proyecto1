from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

import serial

if TYPE_CHECKING:
    from .admin import AdministradorTramas


class PuertoSerialEmisor:
    def __init__(self, port: str, timeout: float = 10.0) -> None:
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

    @staticmethod
    def _seq_of(frame: bytes) -> int:
        return frame[1]

    @staticmethod
    def _inter_frame_delay(payload_size: int, speed_bps: int) -> float:
        """
        Total time the Nano needs before it is ready to accept the next frame:
          1. Reading the current frame from USB (blocks until all bytes arrive)
          2. Forwarding it via SoftwareSerial (2 bytes per original byte, blocking write)
          3. Loop overhead: recibirTrama() check + delay(50 ms)
        The next frame must not start arriving until the Nano is done,
        otherwise the 64-byte UART hardware buffer overflows.
        """
        frame_bytes = payload_size + 7                      # header(4) + payload + checksum(2) + trailer(1)
        usb_recv_s = (frame_bytes * 10) / speed_bps         # Nano reads frame from USB
        softserial_bytes = frame_bytes * 2                  # Nano sends 2 bytes per original byte
        transit_s = (softserial_bytes * 10) / speed_bps     # Nano forwards via SoftwareSerial
        return usb_recv_s + transit_s + 0.060               # +60 ms for loop overhead

    def enviar_transferencia(
        self,
        admin: AdministradorTramas,
        connection_frame: bytes,
        bursts: list[list[bytes]],
    ) -> None:
        inter_frame_s = self._inter_frame_delay(
            admin.session.payload_size, admin.session.speed_bps
        )
        print(
            f"[Serial] Inter-frame delay: {inter_frame_s * 1000:.0f} ms "
            f"(P={admin.session.payload_size}B @ {admin.session.speed_bps}bps)"
        )

        # --- Handshake ---
        print(f"[Serial] Enviando handshake ({len(connection_frame)} bytes)...")
        self._ser.reset_input_buffer()
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
        print(f"[Serial] Handshake confirmado. Iniciando transferencia de {len(bursts)} ráfaga(s)...")

        sleep(0.5)
        self._cambiar_baud(admin.session.speed_bps)

        # --- Sliding-window Go-Back-N (half-duplex: send full burst, then wait) ---
        total_bursts = len(bursts)
        for i, burst in enumerate(bursts):
            burst_to_send = list(burst)

            if i > 0:
                sleep(inter_frame_s)  # let Nano finish forwarding last burst before new frames arrive
            self._ser.reset_input_buffer()

            first_try = True
            while True:
                if not first_try:
                    # Drain Nano pipeline before retransmit: wait for any frames still
                    # in SoftSerial to finish, then flush stale ACK/NACK bytes.
                    sleep(inter_frame_s)
                    self._ser.reset_input_buffer()
                first_try = False

                print(
                    f"[Serial] Ráfaga {i + 1}/{total_bursts}: "
                    f"enviando {len(burst_to_send)} trama(s) "
                    f"(seq {self._seq_of(burst_to_send[0])}–{self._seq_of(burst_to_send[-1])})"
                )

                for j, frame in enumerate(burst_to_send):
                    self._ser.write(frame)
                    if j < len(burst_to_send) - 1:
                        sleep(inter_frame_s)

                # Wait for ONE cumulative response for the whole burst.
                raw = self._leer_respuesta()
                if raw is None:
                    print("[Serial] Timeout — retransmitiendo ráfaga completa...")
                    burst_to_send = list(burst)
                    continue

                try:
                    resp = admin.parse_control_frame(raw)
                except ValueError as exc:
                    print(f"[Serial] Respuesta inválida: {exc} — retransmitiendo...")
                    burst_to_send = list(burst)
                    continue

                if resp["type"] == "ack":
                    print(f"[Serial] ACK ráfaga {i + 1} (seq={resp['sequence']})")
                    break

                # NACK: retransmit from the failed sequence number.
                nack_seq = resp["sequence"]
                burst_seqs = {self._seq_of(f) for f in burst}

                if nack_seq not in burst_seqs:
                    # NACK references a seq outside this burst — burst was received OK.
                    print(
                        f"[Serial] NACK (seq={nack_seq}) confirma ráfaga {i + 1} recibida — avanzando."
                    )
                    break

                print(f"[Serial] NACK (seq={nack_seq}) — retransmitiendo desde seq {nack_seq}...")
                burst_to_send = []
                found = False
                for f in burst:
                    if self._seq_of(f) == nack_seq:
                        found = True
                    if found:
                        burst_to_send.append(f)
                if not burst_to_send:
                    burst_to_send = list(burst)

        print("[Serial] Transferencia completada.")
