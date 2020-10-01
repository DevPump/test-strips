import os
import tempfile

import pytest

from app import create_missing_data_folder, write_data, get_data


def test_data_create():
    return create_missing_data_folder()


def test_get_data():
    result = get_data()
    return result
