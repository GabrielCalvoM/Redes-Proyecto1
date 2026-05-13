from __future__ import annotations

from time import sleep

import serial

from CapaEnlace import AdministradorTramas, ConstructorTramas, FrameType


def read_frame(ser: serial.Serial) -> bytes:
    first = ser.read(1)
    if not first:
        return b""

    frame_type = first[0] & 0x03
    if frame_type == FrameType.CONNECTION:
        rest = ser.read(5)
        if len(rest) != 5:
            return b""
        return first + rest

    if frame_type == FrameType.DATA:
        rest = ser.read(3)
        if len(rest) != 3:
            return b""

        size = int.from_bytes(rest[1:3], "big")
        tail = ser.read(size + 3)
        if len(tail) != size + 3:
            return b""

        return first + rest + tail

    rest = ser.read(4)
    if len(rest) != 4:
        return b""
    return first + rest


def main() -> None:
    ser = serial.Serial("COM4", 9600, timeout=1)
    sleep(2)

    administrador = AdministradorTramas()

    while True:
        frame = read_frame(ser)
        if not frame:
            continue

        try:
            parsed = administrador.describe_frame(frame)
            if parsed["type"] == "connection":
                administrador.configure_session(
                    payload_size=parsed["payload_size"],
                    window_size=parsed["window_size"],
                    speed_bps=parsed["speed_bps"],
                )
                print("Conexion:", parsed)
            elif parsed["type"] == "data":
                payload_text = parsed["payload"].decode("utf-8", errors="replace")
                print(f"Datos seq={parsed['sequence']} size={parsed['size']}: {payload_text!r}")
            else:
                print("Control:", parsed)
        except ValueError as exc:
            print(f"Trama inválida: {frame!r} ({exc})")


if __name__ == "__main__":
    main()