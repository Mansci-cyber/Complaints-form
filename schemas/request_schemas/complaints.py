from marshmallow import fields

from schemas.base import ComplaintBaseSchema


class ComplaintRequestSchema(ComplaintBaseSchema):
    photo = fields.Str(required=True)
    photo_extension = fields.Str(required=True)


