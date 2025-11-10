class Transport:
    def __init__(self, response: bytes) -> None:
        self._response = response

    def read(self, size: int = 1) -> bytes:
        data = self._response[0:size]
        self._response = self._response[size:]

        return data

    def write(self, _: bytes) -> None:
        # stub
        pass
