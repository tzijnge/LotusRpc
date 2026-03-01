import logging

try:
    import serial

    Transport = serial.Serial
except ModuleNotFoundError as e:
    if e.name == "serial":
        log = logging.getLogger(__name__)
        log.error(  # noqa: TRY400
            "Error importing serial transport. Try installing LotusRPC"
            " with optional dependency 'transport_serial': pip install lotusrpc[transport_serial]",
        )
    raise
