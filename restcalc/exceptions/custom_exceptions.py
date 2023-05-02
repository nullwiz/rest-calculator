
# Operations


class OperationExistsException(Exception):
    code = 409
    description = 'Operation already exists.'


class OperationNotFoundException(Exception):
    code = 404
    description = 'Operation not found.'


class InvalidOperationUpdateException(Exception):
    code = 400
    description = 'Invalid operation update.'

# Users


class InvalidPasswordException(Exception):
    code = 400
    description = 'Invalid password.'


class InvalidEmailException(Exception):
    code = 400
    description = 'Invalid email.'


class UserExistsException(Exception):
    code = 409
    description = 'User already exists.'


class UserNotFoundException(Exception):
    code = 404
    description = 'User not found.'


class InvalidUserUpdateException(Exception):
    code = 400
    description = 'Invalid user update.'

# Records


class RecordExistsException(Exception):
    code = 409
    description = 'Record already exists.'


class RecordNotFoundException(Exception):
    code = 404
    description = 'Record not found.'


class InvalidRecordUpdateException(Exception):
    code = 400
    description = 'Invalid record update.'


class ForeignKeyViolationException(Exception):
    code = 400
    description = 'Foreign key violation.'

# Calculator


class InsufficientFundsException(Exception):
    code = 400
    description = 'Insufficient funds.'


# External services

class ExternalServiceException(Exception):
    code = 500
    description = 'External service error.'


# Caching

class TaskNotFoundException(Exception):
    code = 404
    description = 'Task not found'
