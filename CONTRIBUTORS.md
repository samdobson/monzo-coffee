## Development environment

All development should be done against the `dev` branch.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy/?template=https://github.com/samdobson/monzo-coffee/tree/dev)

## Setup

You will need to have installed:

* [Python 3.6](http://install.python-guide.org)
* [pipenv](https://pipenv.readthedocs.io/en/latest/)
* [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

```sh
$ git clone --single-branch -b dev https://github.com/samdobson/monzo-coffee
$ cd monzo-coffee

$ pipenv install

$ python manage.py migrate
$ python manage.py collectstatic

$ heroku local
```
Your app is now accessible on [localhost:5000](http://localhost:5000/).

To deploy to Heroku:

```sh
$ heroku create --region eu
$ git push heroku master
$ heroku open
```

## Design

Monzo-coffee is designed for non-technical end users. Keep it simple. Users should not need to know or care what an oAuth flow or a webhook is.

