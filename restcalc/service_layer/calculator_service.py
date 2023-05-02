"""
This service is basically only one function : to process an operation based on the operation type. 
It's only logical that is a separate service since it uses the operations service to get the operation,
the users service to get the user and the records service to add a record.
"""
from restcalculator.domain import model
from typing import List
from restcalculator.service_layer import unit_of_work
from restcalculator.service_layer.external_services.random_string_service \
    import RandomStringService
from restcalculator.service_layer import calculator_service, records_service, \
    operations_service
from restcalculator.schemas.schemas import RecordSchema
from restcalculator.exceptions.custom_exceptions import InsufficientFundsException
from restcalculator.service_layer.unit_of_work import AbstractUnitOfWork
from restcalculator.exceptions.custom_exceptions import OperationNotFoundException
import io
import csv

record_schema = RecordSchema()


def perform_operation(operation: model.Operation, args):
    op_type = operation.type

    if op_type == model.OperationType.ADDITION.value:
        return sum(args)
    if op_type == model.OperationType.SUBSTRACTION.value:
        return args[0] - sum(args[1:])
    if op_type == model.OperationType.MULTIPLICATION.value:
        return args[0] * args[1]
    if op_type == model.OperationType.DIVISION.value:
        if args[1] == 0:
            raise model.DivisionByZero("Division by zero is not allowed")
        return args[0] / args[1]
    if op_type == model.OperationType.SQUARE_ROOT.value:
        return args[0] ** 0.5
    if op_type == model.OperationType.RANDOM_STRING.value:
        ret = RandomStringService().getString()
        return ret

    raise OperationNotFoundException("Operation not found")


def process_operation(user: model.User, operation: model.Operation, args,
                      uow: unit_of_work.AbstractUnitOfWork) -> float:
    if user.balance < operation.cost:
        raise InsufficientFundsException(
            "Insufficient balance for the operation")
    result = perform_operation(operation, args)
    user.balance -= operation.cost
    uow.users.add(user)
    return result


def process_csv_file(file_stream):
    buffer = io.StringIO()
    while True:
        data = file_stream.read(8192)  # Read 8KB at a time
        if not data:
            break
        decoded_data = data.decode("utf-8")
        buffer.write(decoded_data)
        buffer.seek(0)
        lines = buffer.readlines()
        buffer.truncate(0)
        buffer.seek(0)
        for line in lines[:-1]:
            yield line.strip().split(",")
        buffer.write(lines[-1])
    buffer.seek(0)
    for line in buffer.readlines():
        yield line.strip().split(",")


def process_operation_core(user_id: str, operation_type: str,
                           operation_arguments: List, uow: AbstractUnitOfWork):
    # Get the user
    user = uow.users.get(user_id)
    # Get the operation
    operation = operations_service.get_operation_by_type(operation_type, uow)
    # Process the operation
    print(f'Operation arguments are: {operation_arguments}')
    print(type(operation_arguments))
    result = calculator_service.process_operation(
        user, operation, args=operation_arguments, uow=uow)

    # Generate the record
    record_data = {"user_id": user.id, "operation_id": operation.id, "operation_response": result,
                   "user_balance": user.balance, "amount": operation.cost}

    # Handle edge case: if it is a complex number make it a string.
    if isinstance(result, complex):
        record_data["operation_response"] = str(result)

    record = record_schema.load(record_data)
    records_service.add_record(record, uow)
    uow.commit()

    return {"status": "success", "message": "Operation processed successfully",
            "user_balance": user.balance, "result": str(result)}


def count_rows(file_stream):
    reader = csv.reader(
        io.StringIO(file_stream.read().decode("utf-8")), delimiter=',')
    row_count = sum(1 for row in reader) - 1
    return row_count


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['csv']
