#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.selectable import Select
from loguru import logger

class StatementAbstract(ABC):

    @abstractmethod
    def get_sa_sql(self) -> Select:
        raise NotImplementedError

    def get_raw_sql(self) -> str:
        sa_sql = self.get_sa_sql()
        compiled_sql = sa_sql.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
        return str(compiled_sql)

    def debug_sql(self):
        raw_sql = self.get_raw_sql()
        logger.debug(raw_sql)
