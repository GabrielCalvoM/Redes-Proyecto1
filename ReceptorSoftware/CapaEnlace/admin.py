from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque

from .constructor import ConstructorTramas, FrameType


@dataclass
class SessionConfig:
    payload_size: int = 100
    window_size: int = 3
    speed_bps: int = 9600
    hamming_enabled: bool = False
    sequence_count: int = 0


class AdministradorTramas:
    def __init__(self, constructor: ConstructorTramas | None = None) -> None:
        self.constructor = constructor or ConstructorTramas()
        self.session = SessionConfig()
        self._response_frames: Deque[bytes] = deque()
        self._application_buffer: Deque[bytes] = deque()

    def configure_session(
        self,
        payload_size: int | None = None,
        window_size: int | None = None,
        speed_bps: int | None = None,
        hamming_enabled: bool | None = None,
        sequence_count: int | None = None,
    ) -> None:
        if payload_size is not None:
            self.session.payload_size = payload_size
        if window_size is not None:
            self.session.window_size = window_size
        if speed_bps is not None:
            self.session.speed_bps = speed_bps
        if hamming_enabled is not None:
            self.session.hamming_enabled = hamming_enabled
        if sequence_count is not None:
            self.session.sequence_count = sequence_count & 0xFF

    def parse_incoming_frame(self, frame: bytes) -> dict:
        frame = bytes(frame)
        if len(frame) < 7:
            raise ValueError("Frame too short for receptor")
        if frame[-1] != self.constructor.END_BYTE:
            raise ValueError("Invalid frame terminator")
        if (frame[0] >> 2) != self.constructor.START_BITS:
            raise ValueError("Invalid frame start")

        frame_type = FrameType(frame[0] & 0x03)
        if frame_type == FrameType.CONNECTION:
            return self._parse_connection_frame(frame)
        if frame_type == FrameType.DATA:
            return self._parse_data_frame(frame)
        raise ValueError("Receiver only accepts CONNECTION/DATA frames")

    def _parse_connection_frame(self, frame: bytes) -> dict:
        if len(frame) != 7:
            raise ValueError("Invalid connection frame length")

        header = frame[:4]
        checksum = frame[4:6]
        if not self.constructor.checksum.verify(header, checksum):
            raise ValueError("Invalid connection checksum")

        config_byte = frame[1]
        payload_code = (config_byte >> 6) & 0x03
        window_code = (config_byte >> 4) & 0x03
        speed_code = (config_byte >> 1) & 0x07
        hamming_enabled = bool(config_byte & 0x01)

        if payload_code not in (0, 1, 2):
            raise ValueError("Invalid payload code")
        if window_code not in (0, 1, 2):
            raise ValueError("Invalid window code")
        if speed_code not in (0, 1, 2):
            raise ValueError("Invalid speed code")

        payload_size = {0: 100, 1: 400, 2: 1000}[payload_code]
        window_size = {0: 3, 1: 4, 2: 5}[window_code]
        speed_bps = {0: 4800, 1: 9600, 2: 19200}[speed_code]
        sequence_count = (frame[2] << 8) | frame[3]

        self.configure_session(
            payload_size=payload_size,
            window_size=window_size,
            speed_bps=speed_bps,
            hamming_enabled=hamming_enabled,
            sequence_count=sequence_count,
        )

        return {
            "type": "connection",
            "payload_size": payload_size,
            "window_size": window_size,
            "speed_bps": speed_bps,
            "hamming_enabled": hamming_enabled,
            "sequence_count": sequence_count,
            "raw": frame,
        }

    def _parse_data_frame(self, frame: bytes) -> dict:
        if len(frame) < 7:
            raise ValueError("Invalid data frame length")

        sequence = frame[1]
        size = int.from_bytes(frame[2:4], "big")
        expected_length = 1 + 1 + 2 + size + 2 + 1
        if len(frame) != expected_length:
            raise ValueError("Data frame length does not match payload size")

        payload = frame[4 : 4 + size]
        checksum = frame[4 + size : 6 + size]
        body = frame[: 4 + size]
        if not self.constructor.checksum.verify(body, checksum):
            raise ValueError("Invalid data checksum")

        self._application_buffer.append(payload)
        return {
            "type": "data",
            "sequence": sequence,
            "size": size,
            "payload": payload,
            "raw": frame,
        }

    def build_ack(self, sequence: int) -> bytes:
        return self.constructor.build_ack_frame(sequence)

    def build_nack(self, sequence: int) -> bytes:
        return self.constructor.build_nack_frame(sequence)

    def enqueue_ack(self, sequence: int) -> None:
        self._response_frames.append(self.build_ack(sequence))

    def enqueue_nack(self, sequence: int) -> None:
        self._response_frames.append(self.build_nack(sequence))

    def next_response_frame(self) -> bytes | None:
        if not self._response_frames:
            return None
        return self._response_frames.popleft()

    def has_pending_responses(self) -> bool:
        return bool(self._response_frames)

    def remaining_responses(self) -> int:
        return len(self._response_frames)

    def pop_application_payload(self) -> bytes | None:
        if not self._application_buffer:
            return None
        return self._application_buffer.popleft()

    def describe_frame(self, frame: bytes) -> dict:
        return self.parse_incoming_frame(frame)
