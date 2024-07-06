from setuptools import setup, find_packages

with open("README", 'r') as f:
    long_description = f.read()

setup(
   name='lrpc',
   version='0.1.0',
   description='A code generator for remote procedure calls on embedded systems',
   license="MIT",
   long_description=long_description,
   author='T Zijnge',
   author_email='tzijnge@example.com',
   url="https://github.com/tzijnge/LotusRpc",
   packages=find_packages(),
   package_data={'lrpc.schema': ['lotusrpc-schema.json']},
   include_package_data=True,
   install_requires=['click', 'code-generation', 'pyyaml', 'jsonschema'], #external packages as dependencies
   entry_points = '''
        [console_scripts]
        lotusrpc=lrpc.lotusrpc:generate
        lrpcc=lrpc.lrpcc:cli
    ''',
)