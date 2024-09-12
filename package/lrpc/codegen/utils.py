
def optionally_in_namespace(func):
    '''Decorator to generate code in a namespace or not'''
    def wrapper(self, namespace):
        if namespace:
            with self.file.block(f'namespace {namespace}'):
                func(self)
        else:
            func(self)

    return wrapper
