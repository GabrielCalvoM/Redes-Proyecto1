from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Iterable

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
        self._outgoing_frames: Deque[bytes] = deque()
        self._pending_bursts: Deque[list[bytes]] = deque()

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
            self.session.sequence_count = sequence_count

    def split_payload(self, payload: bytes) -> list[bytes]:
        payload = bytes(payload)
        if not payload:
            return [b""]
        chunk_size = self.session.payload_size
        return [payload[index : index + chunk_size] for index in range(0, len(payload), chunk_size)]

    def split_packets_for_burst(self, packets: Iterable[bytes]) -> list[bytes]:
        chunks: list[bytes] = []
        for packet in packets:
            chunks.extend(self.split_payload(bytes(packet)))
        return chunks

    def prepare_transfer(self, payload: bytes) -> list[bytes]:
        return self.prepare_transfer_from_packets([bytes(payload)])

    def prepare_transfer_from_packets(self, packets: Iterable[bytes]) -> list[bytes]:
        chunks = self.split_packets_for_burst(packets)
        self.session.sequence_count = len(chunks) & 0xFF
        connection_frame = self.constructor.build_connection_frame(
            payload_size=self.session.payload_size,
            window_size=self.session.window_size,
            speed_bps=self.session.speed_bps,
            sequence_count=self.session.sequence_count,
            hamming_enabled=self.session.hamming_enabled,
        )

        data_frames = [
            self.constructor.build_data_frame(sequence, chunk)
            for sequence, chunk in enumerate(chunks)
        ]

        return [connection_frame] + data_frames

    def prepare_bursts_from_packets(self, packets: Iterable[bytes]) -> tuple[bytes, list[list[bytes]]]:
        chunks = self.split_packets_for_burst(packets)
        self.session.sequence_count = len(chunks) & 0xFF

        connection_frame = self.constructor.build_connection_frame(
            payload_size=self.session.payload_size,
            window_size=self.session.window_size,
            speed_bps=self.session.speed_bps,
            sequence_count=self.session.sequence_count,
            hamming_enabled=self.session.hamming_enabled,
        )

        data_frames = [
            self.constructor.build_data_frame(sequence, chunk)
            for sequence, chunk in enumerate(chunks)
        ]

        burst_size = max(1, self.session.window_size)
        bursts = [
            data_frames[index : index + burst_size]
            for index in range(0, len(data_frames), burst_size)
        ]
        return connection_frame, bursts

    def load_transfer(self, payload: bytes) -> None:
        connection_frame, bursts = self.prepare_bursts_from_packets([bytes(payload)])
        self._outgoing_frames = deque([connection_frame])
        self._pending_bursts = deque(bursts)
        self.load_next_burst()

    def load_next_burst(self) -> list[bytes]:
        if not self._pending_bursts:
            return []
        burst = self._pending_bursts.popleft()
        self._outgoing_frames.extend(burst)
        return burst

    def has_pending_bursts(self) -> bool:
        return bool(self._pending_bursts)

    def remaining_bursts(self) -> int:
        return len(self._pending_bursts)

    def next_frame(self) -> bytes | None:
        if not self._outgoing_frames:
            return None
        return self._outgoing_frames.popleft()

    def has_pending_frames(self) -> bool:
        return bool(self._outgoing_frames)

    def remaining_frames(self) -> int:
        return len(self._outgoing_frames)

    def frame_count(self, payload: bytes) -> int:
        return len(self.prepare_transfer(payload))

    def parse_control_frame(self, frame: bytes) -> dict:
        frame = bytes(frame)
        if len(frame) != 5:
            raise ValueError("Invalid ACK/NACK frame length")
        if frame[-1] != self.constructor.END_BYTE:
            raise ValueError("Invalid frame terminator")
        if (frame[0] >> 2) != self.constructor.START_BITS:
            raise ValueError("Invalid frame start")

        frame_type = FrameType(frame[0] & 0x03)
        if frame_type not in (FrameType.ACK, FrameType.NACK):
            raise ValueError("Emitter only accepts ACK/NACK frames")

        body = frame[:2]
        checksum = frame[2:4]
        if not self.constructor.checksum.verify(body, checksum):
            raise ValueError("Invalid ACK/NACK checksum")

        return {
            "type": "ack" if frame_type == FrameType.ACK else "nack",
            "sequence": frame[1],
            "raw": frame,
        }

    def describe_frame(self, frame: bytes) -> dict:
        return self.parse_control_frame(frame)
