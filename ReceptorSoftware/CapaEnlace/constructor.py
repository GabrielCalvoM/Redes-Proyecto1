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

    def __init__(self, checksum: Checksum | None = None) -> None:
        self.checksum = checksum or Checksum()

    def _header_byte(self, frame_type: FrameType) -> int:
        return ((self.START_BITS & 0x3F) << 2) | (int(frame_type) & 0x03)

    def build_ack_frame(self, sequence: int) -> bytes:
        body = bytes([self._header_byte(FrameType.ACK), sequence & 0xFF])
        checksum = self.checksum.calculate(body).to_bytes(2, "big")
        return body + checksum + bytes([self.END_BYTE])

    def build_nack_frame(self, sequence: int) -> bytes:
        body = bytes([self._header_byte(FrameType.NACK), sequence & 0xFF])
        checksum = self.checksum.calculate(body).to_bytes(2, "big")
        return body + checksum + bytes([self.END_BYTE])
