from __future__ import annotations

from enum import IntEnum

from .checksum import Checksum


class FrameType(IntEnum):
    CONNECTION = 0
    DATA = 1
    ACK = 2
    NACK = 3


class ConstructorTramas:
    START_BITS = 0x3F
    END_BYTE = 0x7E

    PAYLOAD_TO_CODE = {100: 0, 400: 1, 1000: 2}
    CODE_TO_PAYLOAD = {0: 100, 1: 400, 2: 1000}

    WINDOW_TO_CODE = {3: 0, 4: 1, 5: 2}
    CODE_TO_WINDOW = {0: 3, 1: 4, 2: 5}

    SPEED_TO_CODE = {4800: 0, 9600: 1, 19200: 2}
    CODE_TO_SPEED = {0: 4800, 1: 9600, 2: 19200}

    def __init__(self, checksum: Checksum | None = None) -> None:
        self.checksum = checksum or Checksum()

    def _header_byte(self, frame_type: FrameType) -> int:
        return ((self.START_BITS & 0x3F) << 2) | (int(frame_type) & 0x03)

    def _encode_payload_size(self, payload_size: int) -> int:
        if payload_size not in self.PAYLOAD_TO_CODE:
            raise ValueError(f"Unsupported payload size: {payload_size}")
        return self.PAYLOAD_TO_CODE[payload_size]

    def _encode_window_size(self, window_size: int) -> int:
        if window_size not in self.WINDOW_TO_CODE:
            raise ValueError(f"Unsupported window size: {window_size}")
        return self.WINDOW_TO_CODE[window_size]

    def _encode_speed(self, speed_bps: int) -> int:
        if speed_bps not in self.SPEED_TO_CODE:
            raise ValueError(f"Unsupported speed: {speed_bps}")
        return self.SPEED_TO_CODE[speed_bps]

    def build_connection_frame(
        self,
        payload_size: int,
        window_size: int,
        speed_bps: int,
        sequence_count: int,
        hamming_enabled: bool = False,
    ) -> bytes:
        header = bytes(
            [
                self._header_byte(FrameType.CONNECTION),
                ((self._encode_payload_size(payload_size) & 0x03) << 6)
                | ((self._encode_window_size(window_size) & 0x03) << 4)
                | ((self._encode_speed(speed_bps) & 0x07) << 1)
                | (1 if hamming_enabled else 0),
                (sequence_count >> 8) & 0xFF,
                sequence_count & 0xFF,
            ]
        )
        checksum = self.checksum.calculate(header).to_bytes(2, "big")
        return header + checksum + bytes([self.END_BYTE])

    def build_data_frame(self, sequence: int, payload: bytes) -> bytes:
        payload = bytes(payload)
        size = len(payload)
        if size > 0xFFFF:
            raise ValueError("Payload too large for a single frame")

        body = bytes([self._header_byte(FrameType.DATA), sequence & 0xFF])
        body += size.to_bytes(2, "big") + payload
        checksum = self.checksum.calculate(body).to_bytes(2, "big")
        return body + checksum + bytes([self.END_BYTE])
