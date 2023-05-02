from typing import Optional, List
from restcalculator.domain import model
from restcalculator.service_layer import unit_of_work
from restcalculator.exceptions.custom_exceptions import RecordNotFoundException
from restcalculator.utils.filter_utility import FilterUtility
from datetime import datetime


def add_record(record: model.Record, uow: unit_of_work.AbstractUnitOfWork):
    record = uow.records.add(record)
    record_id = record.id
    return record_id


def get_record(record_id: str, uow: unit_of_work.AbstractUnitOfWork) -> Optional[model.Record]:
    record = uow.records.get(record_id)
    if not record:
        raise RecordNotFoundException(
            f"Record not found with id {record_id}")
    return record


def list_records(uow: unit_of_work.AbstractUnitOfWork, user_id: str, request_args: dict = None, is_admin=False) -> List[model.Record]:
    records, total_pages = FilterUtility.get_filtered_entities(
        repo=uow.records, model_class=model.Record, request_args=request_args, user_id=user_id, is_admin=is_admin)
    return records, total_pages


def update_record(uow: unit_of_work.AbstractUnitOfWork, record_id: str, operation_id: Optional[str] = None, user_id: Optional[str] = None, amount: Optional[float] = None, user_balance: Optional[float] = None, operation_response: Optional[str] = None):
    record = uow.records.get(record_id)
    if not record:
        raise RecordNotFoundException(
            f"Record not found with id {record_id}")

    update_params = {
        'operation_id': operation_id,
        'user_id': user_id,
        'amount': amount,
        'user_balance': user_balance,
        'operation_response': operation_response,
    }

    for attr, value in update_params.items():
        if value is not None:
            setattr(record, attr, value)
    uow.records.update(record)


def delete_record(record_id: str, uow: unit_of_work.AbstractUnitOfWork):
    record = uow.records.get(record_id)
    record.deleted_at = datetime.now()
    uow.records.update(record)
