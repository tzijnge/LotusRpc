import logging

try:
    import serial

    Transport = serial.Serial
except ImportError:
    log = logging.getLogger(__name__)
    log.error(  # noqa: TRY400
        "Error importing serial transport. Try installing LotusRPC"
        " with optional dependency 'transport_serial': pip install lotusrpc[transport_serial]",
    )
    raise
