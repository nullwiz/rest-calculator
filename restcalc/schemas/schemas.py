""" 
Schemas for the different requests that might come in. This is to simplify
validations and to make sure that the data is in the correct format.
"""
from marshmallow import Schema, fields, validate, ValidationError, validates_schema, post_load
from restcalculator.domain.model import User, Record, Operation

# I understand that schemas here could have been better -- and use one big enough schema constructor instead.

# Operations


def non_negative_float(value):
    if value < 0:
        raise ValidationError("Cost must be a non-negative number")


class OperationSchema(Schema):
    type = fields.String(required=True, validate=validate.OneOf(
        ["substraction", "addition", "multiplication", "division", "square_root", "random_string"]))
    cost = fields.Float(required=True, validate=non_negative_float)
    id = fields.UUID(required=False)

    @post_load
    def make_operation(self, data, **kwargs):
        return Operation(**data)


class DeleteOperationSchema(Schema):
    id = fields.Integer(required=True)


class UpdateOperationSchema(Schema):
    operation_type = fields.String(required=True)
    cost = fields.Float(required=True)

# Users


class UserSchema(Schema):
    id = fields.UUID()
    email = fields.Email()
    balance = fields.Float()
    role = fields.Str()
    deleted_at = fields.DateTime()
    password = fields.Str()


class PostUserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    role = fields.Str(required=False)
    balance = fields.Float(required=False)
    deleted_at = fields.DateTime(required=False)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


class UpdateUserSchema(Schema):
    email = fields.Email(required=False)
    password = fields.Str(required=False)
    role = fields.Str(
        required=False, validate=validate.OneOf(["client", "admin"]))
    balance = fields.Float(required=False)

    @validates_schema
    # not all empty.
    def validate_empty(self, data, **kwargs):
        if not data:
            raise ValidationError("At least one field must be provided.")


# Records


class RecordSchema(Schema):
    id = fields.UUID()
    operation_id = fields.UUID()
    user_balance = fields.Float()
    operation_response = fields.Raw()
    user_id = fields.UUID()
    date = fields.DateTime()
    amount = fields.Float()

    @post_load
    def make_record(self, data, **kwargs):
        return Record(**data)


class PostRecordSchema(Schema):
    operation_id = fields.UUID()
    user_balance = fields.Float()
    operation_response = fields.Raw()
    user_id = fields.UUID()
    date = fields.DateTime(required=False)
    amount = fields.Float()

    @post_load
    def make_record(self, data, **kwargs):
        return Record(**data)


class UpdateRecordSchema(Schema):
    user_id = fields.Integer(required=False)
    date = fields.Date(required=False)
    amount = fields.Float(required=False)
    operation_response = fields.Raw(required=False)
    user_balance = fields.Float(required=False)

# Calculator


class CalculatorSchema(Schema):
    type = fields.String(required=True)
    arguments = fields.List(fields.Float(), required=True,
                            validate=validate.Length(min=1, max=2))

    @validates_schema
    def validate_division_by_zero(self, data, **kwargs):
        operation = data.get('type')
        arguments = data.get('arguments')

        if operation == "division" and len(arguments) == 2 and arguments[1] == 0:
            raise ValidationError(
                "Division by zero is not allowed.", field_name="arguments")


# Auth

class AuthLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


class AuthRegisterAdminSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    admin_password = fields.String(required=True)


# Redis leaky bucket
