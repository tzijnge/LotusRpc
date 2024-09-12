from typing import List, Set

from lrpc.core import LrpcDef, LrpcService, LrpcFun
from lrpc import LrpcVisitor

class FunctionChecker(LrpcVisitor):
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.function_ids: Set = set()
        self.function_names: Set[str] = set()
        self.current_service: str = ""

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.errors.clear()
        self.warnings.clear()
        self.function_ids.clear()
        self.function_names.clear()
        self.current_service = ""

    def visit_lrpc_function(self, function: LrpcFun):
        function_id = function.id()
        name = function.name()

        if function_id in self.function_ids:
            self.errors.append(f'Duplicate function id in service {self.current_service}: {function_id}')

        if name in self.function_names:
            self.errors.append(f'Duplicate function name in service {self.current_service}: {name}')

        if name == (self.current_service + 'ServiceShim'):
            self.errors.append(f'Invalid function name: {name}. This name is incompatible with the generated code for the containing service')

        self.function_ids.add(function_id)
        self.function_names.add(name)

    def visit_lrpc_service(self, service: LrpcService):
        self.current_service = service.name()
        self.function_ids.clear()
        self.function_names.clear()
