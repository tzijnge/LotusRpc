import yaml

class Transport:
    def __init__(self, file_url:str) -> None:
        # print(f"file url: {file_url}")
        self.current_message = bytes()

        with open(file_url, mode="rt", encoding="UTF-8") as f:
            self.server = yaml.safe_load(f)

    def read(self, size: int = 1) -> bytes:
        data = self.current_message[0:size]
        self.current_message = self.current_message[size:]

        # print(f"read data: {size}, {data}")
        return data

    def write(self, data: bytes) -> None:
        # print(f"server data: {self.server}")
        # print(f"write data {data}")

        self.current_message = bytes()

        for a in self.server:
            if data == bytes.fromhex(a["write"]):
                self.current_message = bytes.fromhex(a["read"])
                # print(f"match: {a['cli']}")

if __name__ == "__main__":
    with open("ignitor/test.yaml", mode="rt", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
        print(config)
    args = {"server_file": "ignitor/in.txt"}
    t = Transport(**args)
    print(t.read())
    print(t.read(3))
    print(t.read(3))
    t.write(b"\x04\x05\x06")


# yaml:
# - lrpcc command line
# - bytes to send to server
# - bytes to read from server
# - expected response from lrpcc
