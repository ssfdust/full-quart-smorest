#!/usr/bin/env python
# -*- coding: utf-8 -*-

from quart_trio import QuartTrio
from quart import abort
from quart.views import MethodView
from quart_smorest import Api, Blueprint
import marshmallow as ma
import triopg

app = QuartTrio(__name__)
app.config['OPENAPI_VERSION'] = '3.0.2'
api = Api(app)
blp = Blueprint('pets',
                'pets',
                url_prefix='/pets',
                description='Operations on pets')


class ItemNotFoundError(Exception):
    pass


class PetSchema(ma.Schema):
    id = ma.fields.Int(dump_only=True)
    name = ma.fields.String()


class PetQueryArgsSchema(ma.Schema):
    name = ma.fields.String()


class Pet:

    _list = [
        {"id": 1, "name": "test"},
        {"id": 2, "name": "test2"},
        {"id": 3, "name": "test3"},
        {"id": 4, "name": "test4"},
        {"id": 5, "name": "test5"},
        {"id": 6, "name": "test6"},
        {"id": 7, "name": "test7"},
        {"id": 8, "name": "test8"},
        {"id": 9, "name": "test9"}
    ]

    @classmethod
    def get(cls, filters):
        if filters and filters["name"]:
            return [item for item in cls._list if item["name"] == filters["name"]]
        return cls._list

    @classmethod
    def create(cls, name=""):
        next_id = max(cls._list, key="id") + 1
        cls._list.append({"id": next_id, "name": name})

    @classmethod
    def get_by_id(cls, pet_id):
        found = None
        for item in cls._list:
            if item["id"] == pet_id:
                found = item
                break
        else:
            raise ItemNotFoundError
        return found


@blp.route('/')
class Pets(MethodView):
    @blp.arguments(PetQueryArgsSchema, location='query')
    @blp.response(PetSchema(many=True))
    async def get(self, args):
        """List pets"""
        async with triopg.connect("postgres://megalith-security") as conn:
            cursor = await conn.execute(
                "select * from users"
            )
            print(cursor.fetchall())
        return Pet.get(filters=args)

    @blp.arguments(PetSchema)
    @blp.response(PetSchema, code=201)
    async def post(self, new_data):
        """Add a new pet"""
        item = Pet.create(**new_data)
        return item


@blp.route('/<int:pet_id>')
class PetsById(MethodView):
    @blp.response(PetSchema)
    async def get(self, pet_id):
        """Get pet by ID"""
        try:
            item = Pet.get_by_id(pet_id)
        except ItemNotFoundError:
            abort(404)
        return item

    @blp.arguments(PetSchema)
    @blp.response(PetSchema)
    async def put(self, update_data, pet_id):
        """Update existing pet"""
        try:
            item = Pet.get_by_id(pet_id)
        except ItemNotFoundError:
            abort(404)
        item.update(update_data)
        return item

    @blp.response(code=204)
    async def delete(self, pet_id):
        """Delete pet"""
        try:
            Pet.get_by_id(pet_id)
        except ItemNotFoundError:
            abort(404)


api.register_blueprint(blp)
app.run()
