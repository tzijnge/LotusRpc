from pathlib import Path
from typing import Final, Literal, NotRequired

import yaml
from pydantic import TypeAdapter
from typing_extensions import TypedDict

TransportParamsType = dict[str, str | int | bool | float | bytes]


DEFINITION_URL: Final = "definition_url"
DEFINITION_FROM_SERVER: Final = "definition_from_server"
TRANSPORT_TYPE: Final = "transport_type"
TRANSPORT_PARAMS: Final = "transport_params"
LOG_LEVEL: Final = "log_level"
CHECK_SERVER_VERSION: Final = "check_server_version"


class LrpccConfigDict(TypedDict):
    definition_url: NotRequired[str]
    definition_from_server: NotRequired[Literal["always", "never", "once"]]
    transport_type: str
    transport_params: NotRequired[TransportParamsType]
    log_level: NotRequired[Literal["CRITICAL", "FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG", "NOTSET"]]
    check_server_version: NotRequired[bool]


# pylint: disable=invalid-name
LrpccConfigValidator = TypeAdapter(LrpccConfigDict)


class LrpccConfig:
    def __init__(self, raw: LrpccConfigDict) -> None:
        LrpccConfigValidator.validate_python(raw, strict=True, extra="forbid")

        definition_url_not_provided = DEFINITION_URL not in raw
        self._definition_url = Path() if definition_url_not_provided else Path(raw[DEFINITION_URL]).resolve()
        self._definition_from_server = raw.get(DEFINITION_FROM_SERVER, "never")

        if self._definition_from_server == "never":
            if definition_url_not_provided:
                self._raise_for_missing_definition_url(raw)
            if not self._definition_url.exists():
                self._raise_when_definition_url_does_not_exist(raw)

        if self._definition_from_server == "once" and definition_url_not_provided:
            self._raise_for_missing_definition_url(raw)

        self._transport_type = raw[TRANSPORT_TYPE]
        self._transport_params = raw.get(TRANSPORT_PARAMS, {})
        self._log_level = raw.get(LOG_LEVEL, "INFO")
        self._check_server_version = raw.get(CHECK_SERVER_VERSION, True)

    def _raise_for_missing_definition_url(self, raw: LrpccConfigDict) -> None:
        definition_from_server = self._definition_from_server if DEFINITION_FROM_SERVER in raw else "never (default)"
        raise ValueError(
            f"'{DEFINITION_URL}' must be specified when '{DEFINITION_FROM_SERVER}' is {definition_from_server}",
        )

    def _raise_when_definition_url_does_not_exist(self, raw: LrpccConfigDict) -> None:
        definition_from_server = self._definition_from_server if DEFINITION_FROM_SERVER in raw else "never (default)"
        raise FileNotFoundError(
            f"{self._definition_url} must exist when '{DEFINITION_FROM_SERVER}' is {definition_from_server}",
        )

    @staticmethod
    def load(path: Path) -> "LrpccConfig":
        with path.open(encoding="utf-8") as config_file:
            config: LrpccConfigDict = yaml.safe_load(config_file)
            return LrpccConfig(config)

    @staticmethod
    def create(path: Path, definition_url: str, transport_type: str) -> None:
        config_dict: LrpccConfigDict = {
            DEFINITION_URL: definition_url,
            DEFINITION_FROM_SERVER: "once",
            TRANSPORT_TYPE: transport_type,
            TRANSPORT_PARAMS: {},
            LOG_LEVEL: "INFO",
            CHECK_SERVER_VERSION: True,
        }

        if transport_type == "serial":
            config_dict[TRANSPORT_PARAMS]["port"] = "<PORT>"
            config_dict[TRANSPORT_PARAMS]["baudrate"] = "<BAUDRATE>"

        with path.open(mode="wt+", encoding="utf-8") as lrpcc_config_file:
            yaml.safe_dump(config_dict, lrpcc_config_file)

    def definition_url(self) -> Path:
        return self._definition_url

    def definition_from_server(self) -> str:
        return self._definition_from_server

    def transport_type(self) -> str:
        return self._transport_type

    def transport_params(self) -> TransportParamsType:
        return self._transport_params

    def log_level(self) -> str:
        return self._log_level

    def check_server_version(self) -> bool:
        return self._check_server_version
