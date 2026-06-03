import gc
import warnings
from collections.abc import Generator

import pytest


@pytest.fixture(autouse=True)
def force_gc_within_test() -> Generator[None, None, None]:
    """Force GC while inside the test's execution context.

    click.File handles opened by CliRunner may not be closed until GC runs.
    On Python 3.14 that GC fires at session teardown (outside any per-test
    warning filter), producing spurious ResourceWarning errors. Collecting
    here keeps the teardown clean.
    """
    yield
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ResourceWarning)
        gc.collect()
