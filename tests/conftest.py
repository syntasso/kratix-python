# tests/conftest.py
from pathlib import Path

import pytest

import kratix_sdk as ks


@pytest.fixture(autouse=True)
def reset_dirs(tmp_path):
    """
    Keep global dirs isolated per test.
    """
    in_dir: Path = tmp_path / "in"
    out_dir: Path = tmp_path / "out"
    meta_dir: Path = tmp_path / "meta"
    in_dir.mkdir()
    out_dir.mkdir()
    meta_dir.mkdir()
    ks.set_input_dir(in_dir)
    ks.set_output_dir(out_dir)
    ks.set_metadata_dir(meta_dir)
    yield
