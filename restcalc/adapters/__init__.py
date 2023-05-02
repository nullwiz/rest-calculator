"""
The term "adapter" in this context does not necessarily refer to the Adapter Pattern; it describes the repositories/orm as
an intermediary between the data access and the business logic layers. 
The repositories serve as adapters to different storage mechanisms,
and provide a unified interface for the rest of the application to work with. Hence you see the repos/ folder and the orm.py
file: it adaplts the domain model to a specific storage technology-- in this case, SQLAlchemy (could be named sqlalchemy_orm.py)

"""
