"""
    可能有一天会转为Rust语言实现，先熟悉一下Trait
"""

from functools import wraps
from .abstract import StatementAbstract


class SAQuery(StatementAbstract):

    def get_sa_sql(self):
        pass


def sql_decorator(cls: SAQuery):
    @wraps(cls)
    def wraper(*args, **kwargs):
        def get_sa_sql(self):
            return self.query.statement

        cls.get_sa_sql = get_sa_sql

        return cls(*args, **kwargs)

    return wraper
