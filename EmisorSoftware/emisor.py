import serial
from time import sleep
import ast

if __name__ == "__main__":
    ser = serial.Serial("COM6", 9600)
    sleep(2)

    while True:
        data = input("Enter data: ")

        try:
            # B = data.encode("ascii")
            B = ast.literal_eval(data)
            ser.write(B)
            print(B, "\n")

        except ValueError:
            print("Datos inválidos")