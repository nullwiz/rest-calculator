from setuptools import setup, find_packages

setup(
    name="restcalculator",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={"": ["*.py"]},
    install_requires=[
        'wheel',
        'setuptools',
        'Flask',
        'SQLAlchemy',
        'Werkzeug==2.3.2',
        'markupsafe==2.1.1',
        'sqlalchemy',
        'python-dotenv',
        'psycopg2-binary',
        'autopep8',
        'Flask-JWT-Extended',
        'pyopenssl',
        'python-dotenv',
        'marshmallow',
        'bcrypt',
        'flask-talisman',
        'redis',
    ],
)
