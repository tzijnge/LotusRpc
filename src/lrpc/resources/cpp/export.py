from collections.abc import Mapping
from importlib import resources
from importlib.metadata import version
from pathlib import Path
from string import Template

from lrpc.core.settings import LrpcByteType


def create_dir_if_not_exists(target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)


def export(resource: str, output: Path, substitutions: Mapping[str, str] | None = None) -> None:
    resource_path = resources.files(__package__).joinpath(resource)

    with (
        resources.as_file(resource_path) as resource_file,
        resource_file.open(encoding="utf8") as source,
        output.joinpath(resource_file.name).open(mode="w", encoding="utf-8") as dest,
    ):
        v = version("lotusrpc")
        dest.write(f"// This file has been generated with LRPC version {v}\n")

        source_data = Template(source.read())
        dest.write(source_data.substitute(substitutions or {}))


def export_to(output: Path, byte_type: LrpcByteType) -> None:
    core_dir = output.joinpath("lrpccore")
    create_dir_if_not_exists(core_dir)

    export("EtlRwExtensions.hpp", core_dir)
    export("Server.hpp", core_dir)
    export("Service.hpp", core_dir)
    export("MetaError.hpp", core_dir)
    export(
        "LrpcTypes.hpp",
        core_dir,
        {
            "byte_type": byte_type,
            "byte_include": _byte_include(byte_type),
        },
    )


def _byte_include(byte_type: LrpcByteType) -> str:
    if byte_type == "etl::byte":
        return "#include<etl/byte.h>"
    return ""
