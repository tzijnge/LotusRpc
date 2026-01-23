from pathlib import Path

import yaml


class Transport:
    def __init__(self, file_url: str) -> None:
        self.current_message = b""

        with Path(file_url).open(encoding="UTF-8") as f:
            self.server = yaml.safe_load(f)

    def read(self, size: int = 1) -> bytes:
        data = self.current_message[0:size]
        self.current_message = self.current_message[size:]

        return data

    def write(self, data: bytes) -> None:
        self.current_message = b""

        for a in self.server:
            if data == bytes.fromhex(a["write"]):
                self.current_message = bytes.fromhex(a["read"])
                return

        raise ValueError(f"Received unexpected data of length {len(data)}: {data!r}")
