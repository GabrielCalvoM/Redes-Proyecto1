class Checksum:
    @staticmethod
    def calculate(data: bytes) -> int:
        data = bytes(data)
        if len(data) % 2:
            data += b"\x00"

        total = 0
        for index in range(0, len(data), 2):
            word = (data[index] << 8) | data[index + 1]
            total += word
            total = (total & 0xFFFF) + (total >> 16)

        return (~total) & 0xFFFF

    @staticmethod
    def append(data: bytes) -> bytes:
        checksum = Checksum.calculate(data)
        return bytes(data) + checksum.to_bytes(2, "big")

    @staticmethod
    def verify(data: bytes, checksum: bytes | int) -> bool:
        if isinstance(checksum, int):
            checksum_value = checksum & 0xFFFF
        else:
            checksum_bytes = bytes(checksum)
            if len(checksum_bytes) != 2:
                return False
            checksum_value = int.from_bytes(checksum_bytes, "big")

        return Checksum.calculate(data) == checksum_value
