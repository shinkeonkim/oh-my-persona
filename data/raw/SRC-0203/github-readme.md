# docker_o_template

creator: koa

## how to set development environment

### use docker
- set `USE_DOCKER=TRUE` in `.env` file
- run `docker-compose up -d --build`

### not use docker
```bash
> python -m venv venv
> source venv/bin/activate

> pip install -r requirements.txt
> python manage.py migrate
> python manage.py collectstatic
> python manage.py runserver
```

## extension pages
- http://127.0.0.1:{PORT}/silk/
  - monitoring site
- http://127.0.0.1:{PORT}/explorer/
  - SQL explorer site
## how to write .env file
```
## django settings
PORT="1234"
DEBUG="TRUE" # debug mode
SECRET_KEY="js$5hdno(%^87o-6z^rmxay*jlq!#m(7fv0c%sku!+)u_f5#e!"

## deploy settings
DEPLOY_URL="*"

## docker settings
USE_DOCKER="FALSE" # USE docker-compose

## postgress settings
POSTGRES_NAME="postgress"
POSTGRES_USER="postgress"
POSTGRES_PASSWORD="qwer1234!"
POSTGRES_PORT="5435"
POSTGRES_CHECK_TIMEOUT="30"
POSTGRES_CHECK_INTERVAL="1"

EMAIL_HOST="smtp.gmail.com"
EMAIL_PASSWORD="DUMMY_EMAIL_PASSWORD"
EMAIL_ADDRESS="DUMMY_EMAIL"
DEFAULT_FORM_MAIL="DUMMY_EMAIL_NAME"

```

## test coverage commad
### run test
> coverage run  manage.py test

### coverage cli report
> coverage report

### coverage html report
> coverage html
