import hashlib
import shutil
from urllib import request
from contextlib import closing
from os import path
import ssl
from shutil import copytree
import tempfile
import click

ssl._create_default_https_context = ssl._create_unverified_context

ARM_GCC_VERSION = "14.3.rel1"
ARM_GCC_NAME = f"arm-gnu-toolchain-{ARM_GCC_VERSION}-x86_64-arm-none-eabi"

ARM_GCC = {
    "url": f"https://developer.arm.com/-/media/Files/downloads/gnu/{ARM_GCC_VERSION}/binrel/{ARM_GCC_NAME}.tar.xz",
    "hash": "8f6903f8ceb084d9227b9ef991490413014d991874a1e34074443c2a72b14dbd",
}


def get_hash(file_name: str) -> str:
    h = hashlib.sha256()

    with open(file_name, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            h.update(data)

    return h.hexdigest()


@click.command()
@click.option("-d", "--destination", type=click.Path(), required=True, help="Destination path")
def install_arm_gcc(destination: str) -> None:
    with tempfile.TemporaryDirectory() as temp:
        file_name = path.join(temp, "arm_gcc.tar.xz")

        with closing(request.urlopen(ARM_GCC["url"])) as r:
            with open(file_name, "wb") as f:
                shutil.copyfileobj(r, f)

        assert ARM_GCC["hash"] == get_hash(file_name), f"Invalid hash for {file_name}"

        shutil.unpack_archive(file_name, temp)
        copytree(path.join(temp, ARM_GCC_NAME), destination)


if __name__ == "__main__":
    install_arm_gcc()
