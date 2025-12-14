import hashlib
import shutil
import ssl
import tempfile
from contextlib import closing
from pathlib import Path
from shutil import copytree
from urllib import request

import click

ssl._create_default_https_context = ssl._create_unverified_context  # type: ignore[assignment]  # noqa: SLF001  # pylint: disable=protected-access

ARM_GCC_VERSION = "14.3.rel1"
ARM_GCC_NAME = f"arm-gnu-toolchain-{ARM_GCC_VERSION}-x86_64-arm-none-eabi"

ARM_GCC = {
    "url": f"https://developer.arm.com/-/media/Files/downloads/gnu/{ARM_GCC_VERSION}/binrel/{ARM_GCC_NAME}.tar.xz",
    "hash": "8f6903f8ceb084d9227b9ef991490413014d991874a1e34074443c2a72b14dbd",
}


def get_hash(file: Path) -> str:
    h = hashlib.sha256()

    with file.open("rb") as f:
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
        file = Path(temp).joinpath("arm_gcc.tar.xz")

        with closing(request.urlopen(ARM_GCC["url"])) as r, file.open("wb") as f:  # noqa: S310
            shutil.copyfileobj(r, f)

        if ARM_GCC["hash"] != get_hash(file):
            raise ValueError(f"Invalid hash for {file}")

        shutil.unpack_archive(file, extract_dir=temp)
        copytree(temp + "/" + ARM_GCC_NAME, destination)


if __name__ == "__main__":
    install_arm_gcc()
