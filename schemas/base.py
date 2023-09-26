from marshmallow import Schema, fields, validate


class UserRequestBase(Schema):
    password = fields.String(required=True)
    email = fields.Email(required=True)


class ComplaintBaseSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=100))

