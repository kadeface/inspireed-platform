"""
基础测试 - 确保测试框架正常工作
"""

import pytest


def test_import_app():
    """测试能够导入app模块"""
    from app import main

    assert main is not None


def test_basic_math():
    """基础数学测试 - 确保pytest正常工作"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_string_operations():
    """字符串操作测试"""
    test_str = "Inspireed Platform"
    assert "Platform" in test_str
    assert test_str.startswith("Inspireed")
    assert len(test_str) > 0


@pytest.mark.parametrize(
    "input,expected",
    [
        (1, 2),
        (2, 4),
        (3, 6),
        (10, 20),
    ],
)
def test_double(input, expected):
    """参数化测试示例"""
    assert input * 2 == expected
