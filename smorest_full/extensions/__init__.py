#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import sa


def init_app(app):
    sa.init_app(app)
