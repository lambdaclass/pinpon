.PHONY: shell

init:
	pipenv --three && pipenv install

shell:
	pipenv run python manage.py shell -i ipython

server:
	pipenv run python manage.py runserver

migrate:
	pipenv run python manage.py makemigrations pinpon && pipenv run python manage.py migrate
