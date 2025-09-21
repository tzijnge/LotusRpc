class Transport:
    def __init__(self) -> None:
        self.reponse = bytes()

    def read(self, size: int = 1) -> bytes:
        data = self.reponse[0:size]
        self.reponse = self.reponse[size:]

        return data

    def write(self, _: bytes) -> None:
        # stub
        pass
