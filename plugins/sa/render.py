#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.engine.result import ResultProxy
from tabulate import tabulate

class TableRender:

    @staticmethod
    def _render_data_table(cursor: ResultProxy, size: int) -> str:
        records = cursor.fetchmany(size)
        headers = cursor.keys()
        return tabulate(records, headers=headers, tablefmt="fancygrid")
