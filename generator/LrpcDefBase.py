from abc import ABC, abstractmethod


class LrpcDefBase(ABC):
    def name(self):
        pass

    def namespace(self):
        pass

    def rx_buffer_size(self):
        pass

    def tx_buffer_size(self):
        pass

    def services(self):
        pass

    def max_service_id(self):
        pass

    def structs(self):
        pass

    def enums(self):
        pass

    def constants(self):
        pass