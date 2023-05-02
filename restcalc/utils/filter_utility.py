from typing import Dict, Type, Optional, List, Tuple
"""
I understand that this code is atm coupled to the SQLAlchemy query object. 
To make it more generic, I would implement an AbstractQuery class and
a SQLAlchemyQuery class. That way on line  97, i would do something like:
def get_filtered_entities(repo, query_cls: Type[AbstractQuery], model_class: Type, request_args: Dict, user_id: Optional[str] = None, is_admin: bool = False) -> Tuple[List[T], int]:
        (...)
        query = repo.get_filtered_query(filters=request_filters)
        abstract_query = query_cls(query)
        total_records = abstract_query.count()
        total_pages = FilterUtility.calculate_total_pages(total_records, page_size)

        paginated_query = FilterUtility.apply_pagination(abstract_query, page, page_size)
        results = paginated_query.all()

        (...)
The SQLAlchemyQuery class would implement: 
    def all(self) -> List[T]: # any type 
        return self.query.all()

Then create a factory for the query class based off configuration of flask.. and do something like:
query = create_query_class(app)


In the services we could do:
   def list_records(uow: unit_of_work.AbstractUnitOfWork, user_id: str, request_args: dict = None, is_admin=False) -> List[model.Record]:
        query_cls = create_query_class()
        records, total_pages = FilterUtility.get_filtered_entities(
        repo=uow.records, query_cls=query_cls, model_class=model.Record, request_args=request_args, user_id=user_id, is_admin=is_admin)
        return records, total_pages

This way we can easily implement a new query class for a different DB. Coming soon B)
"""


class FilterUtility:
    @staticmethod
    def filter_request_args(request_args: Dict, model_class: Type) -> Dict:
        if not request_args:
            return {}

        filter_keys = [key for key in request_args.keys() if key not in [
            "page", "page_size", "fields"]]

        # Validate filter keys
        for key in filter_keys:
            if not hasattr(model_class, key):
                raise KeyError(f"Invalid filter key: {key}")

        return {key: request_args.get(key) for key in filter_keys}

    @staticmethod
    def apply_pagination(query, page: int, page_size: int):
        offset = (page - 1) * page_size
        return query.offset(offset).limit(page_size)

    @staticmethod
    def get_selected_fields(request_args: Dict, model_class: Type) -> Optional[List[str]]:
        selected_fields = request_args.get("fields", None)
        if selected_fields:
            selected_fields = selected_fields.split(',')
            for field in selected_fields:
                if not hasattr(model_class, field):
                    raise ValueError(f"Invalid selected field: {field}")
        return selected_fields

    @staticmethod
    def validate_page_and_page_size(request_args: Dict) -> Tuple[int, int]:
        try:
            # Default values could be defined by DB here.
            page = int(request_args.get("page", 1))
            page_size = int(request_args.get("page_size", 10))
        except ValueError:
            raise ValueError(
                "Invalid 'page' or 'page_size' value. Please provide valid integers.")
        return page, page_size

    @staticmethod
    def calculate_total_pages(record_count: int, page_size: int) -> int:
        return (record_count + page_size - 1) // page_size

    @staticmethod
    def get_filtered_entities(repo, model_class: Type, request_args: Dict, user_id: Optional[str] = None, is_admin: bool = False):
        # Validate page_size and page
        try:
            page, page_size = FilterUtility.validate_page_and_page_size(
                request_args)
        except ValueError as e:
            raise ValueError(str(e))
        request_filters = FilterUtility.filter_request_args(
            request_args, model_class)
        selected_fields = FilterUtility.get_selected_fields(
            request_args, model_class)

        if not is_admin and user_id:
            request_filters["user_id"] = user_id

        query = repo.get_filtered_query(filters=request_filters)

        # Calculate total pages
        total_records = query.count()
        total_pages = FilterUtility.calculate_total_pages(
            total_records, page_size)

        paginated_query = FilterUtility.apply_pagination(
            query, page, page_size)
        results = paginated_query.all()

        if selected_fields:
            results = [{field: getattr(item, field)
                        for field in selected_fields} for item in results]

        return results, total_pages
