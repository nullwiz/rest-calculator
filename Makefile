# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test

build: package
	docker-compose build
package: 
	pip uninstall -y restcalculator
	python setup.py sdist bdist_wheel
	pip install dist/restcalculator-0.1-py3-none-any.whl
	rm -rf build dist restcalculator.egg-info
build-local-db:
	python restcalculator/setup_scripts/setup.py --teardown 
build-prod-db:
	python restcalculator/setup_scripts/setup.py --teardown --database-uri $(db)
up:
	docker-compose up -d 
	aws --profile localstack --endpoint-url http://localhost:4566 s3api create-bucket --bucket buckeeto 
	aws --profile localstack --endpoint-url http://localhost:4566 sqs create-queue --queue-name opworker
	make build-local-db
up-db: 
	docker-compose up -d postgres

down:
	docker-compose down --remove-orphans

test: 
	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/

unit-tests: 
	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/unit

e2e-tests: 
	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/e2e

logs:
	docker-compose logs app | tail -400

ruff:
	ruff .	
deploy:
	. ./predeploy.sh && cd restcalculator/ && serverless deploy 

lambda:
	. ./predeploy_local.sh && cd restcalculator/ && python worker/local_middleware.py 
