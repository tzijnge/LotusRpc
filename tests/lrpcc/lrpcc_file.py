import yaml


class Transport:
    def __init__(self, file_url: str) -> None:
        self.current_message = bytes()

        with open(file_url, mode="rt", encoding="UTF-8") as f:
            self.server = yaml.safe_load(f)

    def read(self, size: int = 1) -> bytes:
        data = self.current_message[0:size]
        self.current_message = self.current_message[size:]

        return data

    def write(self, data: bytes) -> None:
        self.current_message = bytes()

        for a in self.server:
            if data == bytes.fromhex(a["write"]):
                self.current_message = bytes.fromhex(a["read"])
