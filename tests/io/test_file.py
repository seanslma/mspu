import json

import pytest

from mspu.io import read_json, read_text, write_json, write_text


def test_write_read_text(tmp_path):
    p = tmp_path / 'hello.txt'
    write_text(str(p), 'hello world')
    assert p.read_text() == 'hello world'
    assert read_text(str(p)) == 'hello world'


def test_write_text_mkdir(tmp_path):
    p = tmp_path / 'nested' / 'dir' / 'file.txt'
    write_text(str(p), 'x', mkdir=True)
    assert p.exists()


def test_write_text_no_mkdir(tmp_path):
    p = tmp_path / 'nested' / 'file.txt'
    with pytest.raises(FileNotFoundError):
        write_text(str(p), 'x', mkdir=False)


def test_write_read_json(tmp_path):
    p = tmp_path / 'data.json'
    data = {'name': 'mspu', 'nums': [1, 2, 3]}
    write_json(str(p), data)
    assert read_json(str(p)) == data
    # file content is valid JSON with indent
    assert json.loads(p.read_text()) == data


def test_write_json_mkdir(tmp_path):
    p = tmp_path / 'a' / 'b' / 'data.json'
    write_json(str(p), {'k': 'v'}, mkdir=True)
    assert p.exists()


def test_read_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_text(str(tmp_path / 'nope.txt'))
    with pytest.raises(FileNotFoundError):
        read_json(str(tmp_path / 'nope.json'))
