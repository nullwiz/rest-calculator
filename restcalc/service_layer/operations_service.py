from typing import Optional, List, Dict
from restcalculator.domain import model
from restcalculator.service_layer import unit_of_work
from restcalculator.exceptions.custom_exceptions import OperationNotFoundException
from restcalculator.utils.filter_utility import FilterUtility


def get_operation(operation_id: str, uow: unit_of_work.AbstractUnitOfWork) -> Optional[model.Operation]:
    """
    Gets an operation by id
    """
    operation = uow.operations.get(operation_id)
    return operation


def get_operation_by_type(operation_type: str, uow: unit_of_work.AbstractUnitOfWork) -> Optional[model.Operation]:
    """
    Gets an operation by type
    """
    operation, _ = FilterUtility.get_filtered_entities(
        uow.operations, model.Operation, {"type": operation_type})

    if len(operation) == 0:
        raise OperationNotFoundException
    # It's always one -- they are unique.
    return operation[0]


def list_operations(uow: unit_of_work.AbstractUnitOfWork, request_args: Dict) -> List[model.Operation]:
    """
    Lists operations based on the request args
    """
    operations, total_pages = FilterUtility.get_filtered_entities(
        uow.operations, model.Operation, request_args)
    return operations, total_pages


def add_operation(operation_type: str, cost: float, uow: unit_of_work.AbstractUnitOfWork) -> model.Operation:
    """Add a new operation."""
    operation = model.Operation(type=operation_type, cost=cost)
    uow.operations.add(operation)
    return operation


def update_operation(operation_id: str, operation_type: str, new_cost: float, uow: unit_of_work.AbstractUnitOfWork) -> model.Operation:
    """Update an existing operation."""
    operation = uow.operations.get(operation_id)
    update_params = {
        "operation_type": operation_type,
        "cost": new_cost
    }
    for attr, value in update_params.items():
        if value is not None:
            setattr(operation, attr, value)
    operation = uow.operations.update(operation)
    return operation


def delete_operation(operation_id: str, uow: unit_of_work.AbstractUnitOfWork) -> None:
    """Delete an existing operation."""
    operation = uow.operations.get(operation_id)
    uow.operations.delete(operation)
    uow.commit()
