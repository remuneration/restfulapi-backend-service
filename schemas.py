from marshmallow import Schema, fields

class PlainItemSchema(Schema):
    item_id = fields.Int(dump_only=True)
    item_name = fields.Str(required=True)
    price = fields.Float(required=True)

class PlainStoreSchema(Schema):
    store_id = fields.Int(dump_only=True)
    store_name = fields.Str(required=True)

class PlainTagSchema(Schema):
    tag_id = fields.Int(dump_only=True)
    tag_name = fields.Str()

class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    item = fields.List(fields.Nested(PlainItemSchema()), attribute="items",dump_only=True)

class StoreSchema(PlainStoreSchema):
    item = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tag = fields.List(fields.Nested(PlainTagSchema()), dump_only= True)

class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tag = fields.List(fields.Nested(PlainTagSchema()), attribute="tags", dump_only=True)

class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)

class ItemUpdateSchema(Schema):
    item_name = fields.Str()
    price = fields.Float()
    store_id = fields.Int()

class StoreUpdateSchema(Schema):
    store_name = fields.Str()

class TagUpdateSchema(Schema):
    tag_name = fields.Str()
    store_id = fields.Int()

class UserSchema(Schema):
    user_id = fields.Int(dump_only=True)
    user_name = fields.Str(required=True)
    user_password = fields.Str(required=True, load_only=True)

class Calculation(Schema):
    number = fields.Int(required=True)
    times = fields.Int(required=True)

class Administrator(Schema):
    user_name = fields.Str(required=True)
    admin_password = fields.Str(load_only=True)








