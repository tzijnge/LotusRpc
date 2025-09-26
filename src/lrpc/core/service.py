from typing import Optional, TypedDict, Union
from typing_extensions import NotRequired

from ..visitors import LrpcVisitor
from .function import LrpcFun, LrpcFunDict
from .stream import LrpcStream, LrpcStreamDict


class LrpcServiceDict(TypedDict):
    name: str
    id: int
    functions: NotRequired[list[LrpcFunDict]]
    streams: NotRequired[list[LrpcStreamDict]]
    functions_before_streams: bool


class LrpcService:
    def __init__(self, raw: LrpcServiceDict) -> None:
        assert "name" in raw and isinstance(raw["name"], str)
        assert "id" in raw and isinstance(raw["id"], int)
        assert "functions_before_streams" in raw and isinstance(raw["functions_before_streams"], bool)

        functions = raw.get("functions", [])
        streams = raw.get("streams", [])

        assert (len(functions) != 0) or (len(streams) != 0)

        if "functions" in raw:
            assert isinstance(raw["functions"], list)

        if "streams" in raw:
            assert isinstance(raw["streams"], list)

        self.__assign_function_and_stream_ids(functions, streams, raw["functions_before_streams"])

        self.__name = raw["name"]
        self.__id = raw["id"]
        self.__functions = [LrpcFun(f) for f in functions]
        self.__streams = [LrpcStream(s) for s in streams]

    @staticmethod
    def __assign_function_and_stream_ids(
        functions: list[LrpcFunDict], streams: list[LrpcStreamDict], functions_before_streams: bool
    ) -> None:
        last_id = -1

        if functions_before_streams:
            last_id = LrpcService.__assign_function_ids(functions, last_id)
            LrpcService.__assign_stream_ids(streams, last_id)
        else:
            last_id = LrpcService.__assign_stream_ids(streams, last_id)
            LrpcService.__assign_function_ids(functions, last_id)

    @staticmethod
    def __assign_function_ids(
        functions: list[LrpcFunDict],
        last_id: int,
    ) -> int:
        return LrpcService.__assign_ids(functions, last_id)

    @staticmethod
    def __assign_stream_ids(
        streams: list[LrpcStreamDict],
        last_id: int,
    ) -> int:
        return LrpcService.__assign_ids(streams, last_id)

    @staticmethod
    def __assign_ids(items_needing_id: Union[list[LrpcFunDict], list[LrpcStreamDict]], last_id: int) -> int:
        for item in items_needing_id:
            if "id" in item:
                last_id = item["id"]
            else:
                # id field must be present in LrpcFunDict to construct LrpcFun
                # but it is optional when constructing LrpcService. This method
                # makes sure that function IDs are initialized properly
                last_id = last_id + 1  # type: ignore[unreachable]
                item["id"] = last_id

        return last_id

    def accept(self, visitor: LrpcVisitor) -> None:
        visitor.visit_lrpc_service(self)
        for f in self.functions():
            f.accept(visitor)
        for s in self.streams():
            s.accept(visitor)
        visitor.visit_lrpc_service_end()

    def name(self) -> str:
        return self.__name

    def id(self) -> int:
        return self.__id

    def functions(self) -> list[LrpcFun]:
        return self.__functions

    def function_by_name(self, name: str) -> Optional[LrpcFun]:
        for f in self.functions():
            if f.name() == name:
                return f

        return None

    def function_by_id(self, function_id: int) -> Optional[LrpcFun]:
        for f in self.functions():
            if f.id() == function_id:
                return f

        return None

    def streams(self) -> list[LrpcStream]:
        return self.__streams

    def stream_by_name(self, name: str) -> Optional[LrpcStream]:
        for s in self.streams():
            if s.name() == name:
                return s

        return None

    def stream_by_id(self, stream_id: int) -> Optional[LrpcStream]:
        for s in self.streams():
            if s.id() == stream_id:
                return s

        return None
