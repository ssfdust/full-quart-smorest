#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from quart import Quart
from gino.ext.quart import Gino
from smorest_full.extensions.sa import db as db_instance


@pytest.fixture(scope="package")
def db() -> Gino:
    return db_instance


@pytest.fixture(scope="package")
def TestUser(db) -> db_instance.Model:
    class TestUser(db.Model):
        __tablename__ = "users"

        id = db.Column(db.Integer(), primary_key=True)
        nickname = db.Column(db.Unicode(), default="noname")

    return TestUser


@pytest.fixture
async def sa_app(db: Gino) -> Quart:
    app = Quart("test_sa")
    app.config["DB_DSN"] = "postgres://ssfdust@localhost/my-smorest-testing"
    db.init_app(app)
    for func in app.before_first_request_funcs:
        await func()

    async with app.app_context():
        await db.gino.create_all()
        yield app
        await db.gino.drop_all()


@pytest.fixture
async def prepare_users_info(sa_app, db, TestUser):
    await TestUser.create(nickname="tester")
