FLAG_FILE=.init_completed

up:
	docker-compose up -d --build

down:
	docker-compose down

hard_down:
	docker-compose down -v
	rm -f $(FLAG_FILE)

restart:
	docker-compose down
	docker-compose up -d --build

migrate:
	docker-compose exec admin_panel python manage.py migrate

collectstatic:
	docker-compose exec admin_panel python manage.py collectstatic --no-input --clear

createsuperuser:
	-docker-compose exec admin_panel python manage.py createsuperuser --noinput

generate_data:
	docker-compose exec data_generator python src/main.py

init_once:
	@if [ ! -f $(FLAG_FILE) ]; then \
		make up && \
		make migrate && \
		make collectstatic && \
		make createsuperuser && \
		make generate_data && \
		touch $(FLAG_FILE); \
	else \
		make up; \
	fi

test:
	docker-compose -f tests/functional/docker-compose.yml up -d --build && \
	docker-compose -f tests/functional/docker-compose.yml logs -f tests && \
	docker-compose -f tests/functional/docker-compose.yml down -v


test_auth_only:
	docker-compose -f auth/docker-compose_tests.yml up -d --build && \
	docker-compose -f auth/docker-compose_tests.yml logs -f tests && \
	docker-compose -f auth/docker-compose_tests.yml down -v


dev_up:
	docker-compose -f docker-compose_dev.yml up -d --build


dev_down:
	docker-compose -f docker-compose_dev.yml down -v

rebuild: hard_down init_once

re: rebuild

.DEFAULT_GOAL := init_once
