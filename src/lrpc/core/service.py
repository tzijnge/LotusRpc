from typing import cast

from pydantic import TypeAdapter
from typing_extensions import NotRequired, TypedDict

from lrpc.visitors import LrpcVisitor

from .function import LrpcFun, LrpcFunDict, LrpcFunOptionalIdDict
from .stream import LrpcStream, LrpcStreamDict, LrpcStreamOptionalIdDict


class LrpcServiceDict(TypedDict):
    name: str
    id: int
    functions: NotRequired[list[LrpcFunOptionalIdDict]]
    streams: NotRequired[list[LrpcStreamOptionalIdDict]]
    functions_before_streams: bool


class LrpcServiceOptionalIdDict(TypedDict):
    name: str
    id: NotRequired[int]
    functions: NotRequired[list[LrpcFunOptionalIdDict]]
    streams: NotRequired[list[LrpcStreamOptionalIdDict]]
    functions_before_streams: bool


# pylint: disable=invalid-name
LrpcServiceValidator = TypeAdapter(LrpcServiceDict)


class LrpcService:
    def __init__(self, raw: LrpcServiceDict) -> None:
        LrpcServiceValidator.validate_python(raw, strict=True, extra="forbid")

        functions, streams = self._assign_function_and_stream_ids(
            raw.get("functions", []),
            raw.get("streams", []),
            functions_before_streams=raw["functions_before_streams"],
        )

        self._name = raw["name"]
        self._id = raw["id"]
        self._functions = [LrpcFun(f) for f in functions]
        self._streams = [LrpcStream(s) for s in streams]

    @staticmethod
    def _assign_function_and_stream_ids(
        functions: list[LrpcFunOptionalIdDict],
        streams: list[LrpcStreamOptionalIdDict],
        *,
        functions_before_streams: bool,
    ) -> tuple[list[LrpcFunDict], list[LrpcStreamDict]]:
        if (len(functions) == 0) and (len(streams) == 0):
            raise ValueError("A service must have at least one function or stream")

        last_id = -1

        if functions_before_streams:
            last_id = LrpcService._assign_function_ids(functions, last_id)
            LrpcService._assign_stream_ids(streams, last_id)
        else:
            last_id = LrpcService._assign_stream_ids(streams, last_id)
            LrpcService._assign_function_ids(functions, last_id)

        # functions and streams are now converted to LrpcFunDict and LrpcStreamDict respectively
        # This is validated in the LrpcFun and LrpcStream constructors
        return cast(list[LrpcFunDict], functions), cast(list[LrpcStreamDict], streams)

    @staticmethod
    def _assign_function_ids(
        functions: list[LrpcFunOptionalIdDict],
        last_id: int,
    ) -> int:
        return LrpcService._assign_ids(functions, last_id)

    @staticmethod
    def _assign_stream_ids(
        streams: list[LrpcStreamOptionalIdDict],
        last_id: int,
    ) -> int:
        return LrpcService._assign_ids(streams, last_id)

    @staticmethod
    def _assign_ids(
        items_needing_id: list[LrpcFunOptionalIdDict] | list[LrpcStreamOptionalIdDict],
        last_id: int,
    ) -> int:
        for item in items_needing_id:
            if "id" in item:
                last_id = item["id"]
            else:
                last_id = last_id + 1
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
        return self._name

    def id(self) -> int:
        return self._id

    def functions(self) -> list[LrpcFun]:
        return self._functions

    def function_by_name(self, name: str) -> LrpcFun | None:
        for f in self.functions():
            if f.name() == name:
                return f

        return None

    def function_by_id(self, function_id: int) -> LrpcFun | None:
        for f in self.functions():
            if f.id() == function_id:
                return f

        return None

    def streams(self) -> list[LrpcStream]:
        return self._streams

    def stream_by_name(self, name: str) -> LrpcStream | None:
        for s in self.streams():
            if s.name() == name:
                return s

        return None

    def stream_by_id(self, stream_id: int) -> LrpcStream | None:
        for s in self.streams():
            if s.id() == stream_id:
                return s

        return None
