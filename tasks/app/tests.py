# encoding: utf-8
# pylint: disable=invalid-name,unused-argument,too-many-arguments
"""
单元测试相关的Invoke模块
"""
import logging

from invoke import task

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@task(
    default=True,
    help={
        "directory": "单元测试目录",
        "with-cov": "pytest-cov支持 （默认：否）",
        "cov": "cov检测目录(当启用pytest-cov时必填)",
        "with-pdb": "开启pdb支持 （默认：否）",
    },
)
def tests(context, directory="tests", with_cov=False, cov="", with_pdb=False):
    """
    对项目进行单元测试
    """
    import pytest

    command = [directory]
    return pytest.main(command)
