import serial
from time import sleep

if __name__ == "__main__":
    ser = serial.Serial("COM4", 9600)
    sleep(2)

    while True:
        linea = ser.read(6)

        if linea:
            try:
                print(f"Datos: {linea}\n")

            except ValueError:
                print("Datos inválidos:", linea)