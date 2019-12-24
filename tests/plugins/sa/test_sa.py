#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import pyperclip
from loguru import logger

from tests.utils.injection import inject_logger
from tests.utils.uniqueue import UniqueQueue

from smorest_full.plugins.sa import (
    query_decorator,
    SAQuery,
    SAStatement,
    sql_decorator,
)


pytestmark = pytest.mark.asyncio


@pytest.mark.usefixtures("sa_app")
class TestSAStatement:
    assert_sql = "SELECT users.id, users.nickname \nFROM users"

    async def _get_UserQuery(self, TestUser):
        @sql_decorator
        class UserQuery(SAStatement):
            def __init__(self):
                self.sa_sql = TestUser.query

        return UserQuery()

    async def _get_debug_sql(self):
        queue = UniqueQueue()
        return queue.get(timeout=1)

    async def test_debug_sql(self, TestUser):
        inject_logger(logger)

        user_query = await self._get_UserQuery(TestUser)
        user_query.debug_sql()

        assert (
            pyperclip.paste() == self.assert_sql
            and await self._get_debug_sql() == "\n" + self.assert_sql
        )

    async def test_render_table(self, TestUser, prepare_users_info):
        user_query = await self._get_UserQuery(TestUser)
        await user_query.render_results()
