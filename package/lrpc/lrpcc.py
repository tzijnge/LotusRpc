''' LRPC client CLI'''
from lrpc.core.definition import LrpcDef
from lrpc.client import ClientCliVisitor

lrpc_def: LrpcDef = LrpcDef.load('testdata/TestServer2.lrpc.yaml')
cli_visitor = ClientCliVisitor()
lrpc_def.accept(cli_visitor)

def cli():
    cli_visitor.root()

if __name__ == "__main__":
    cli()