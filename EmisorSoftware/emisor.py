from __future__ import annotations

import ast
from time import sleep

import serial

from CapaEnlace import AdministradorTramas


def parse_payload(raw_input: str) -> bytes | None:
    raw_input = raw_input.strip()
    if not raw_input:
        return None

    if raw_input.startswith(("b'", 'b"', "[", "(", "{")):
        try:
            parsed = ast.literal_eval(raw_input)
        except (ValueError, SyntaxError):
            return None

        if isinstance(parsed, (bytes, bytearray)):
            return bytes(parsed)
        if isinstance(parsed, str):
            return parsed.encode("utf-8")

    return raw_input.encode("utf-8")


def main() -> None:
    ser = serial.Serial("COM6", 9600, timeout=1)
    sleep(2)

    administrador = AdministradorTramas()

    while True:
        data = input("Enter data (/cfg payload window speed | /quit): ")
        command = data.strip().lower()

        if not command:
            continue
        if command in {"/quit", "quit", "exit"}:
            break

        if command.startswith("/cfg "):
            parts = data.split()
            if len(parts) != 4:
                print("Uso: /cfg <payload:100|400|1000> <ventana:3|4|5> <velocidad:4800|9600|19200>")
                continue

            try:
                payload_size = int(parts[1])
                window_size = int(parts[2])
                speed_bps = int(parts[3])
                administrador.configure_session(
                    payload_size=payload_size,
                    window_size=window_size,
                    speed_bps=speed_bps,
                )
                print(f"Config actualizada: payload={payload_size}, ventana={window_size}, velocidad={speed_bps}")
            except ValueError:
                print("Datos inválidos en /cfg")
            continue

        payload = parse_payload(data)
        if payload is None:
            print("Datos inválidos")
            continue

        frames = administrador.prepare_transfer(payload)
        print(f"Frames a enviar: {len(frames)}")

        for frame in frames:
            ser.write(frame)
            try:
                summary = administrador.describe_frame(frame)
                print(summary)
            except ValueError:
                print(frame)


if __name__ == "__main__":
    main()