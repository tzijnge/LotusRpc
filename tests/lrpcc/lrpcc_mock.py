class Transport:
    def __init__(self) -> None:
        self.response = bytes()

    def read(self, size: int = 1) -> bytes:
        data = self.response[0:size]
        self.response = self.response[size:]

        return data

    def write(self, _: bytes) -> None:
        # stub
        pass
