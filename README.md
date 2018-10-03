# Monzo Coffee

Advanced transaction tagging for Monzo.

Powered by [monzo-python](https://github.com/muyiwaolu/monzo-python).

## Quick Start Deployment

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

You will be prompted for a *Monzo Access Token* which can be obtained via the [Monzo Developer Portal](https://developers.monzo.com)

The password is stored as a configuration variable in Heroku.

Consult the [quickstart guide](https://monzo-coffee.readthedocs.io/en/latest/) for a detailed walkthrough.

## Local development

You will need to have installed [Python 3.6](http://install.python-guide.org), [pipenv](https://pipenv.readthedocs.io/en/latest/), the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) and [Postgres](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup).

```sh
$ git clone https://github.com/samdobson/monzo-coffee
$ cd monzo-coffee

$ pipenv install

$ createdb monzocoffee

$ python manage.py migrate
$ python manage.py collectstatic

$ heroku local
```

Your app should now be running on [localhost:5000](http://localhost:5000/).


## Advanced deployment

```sh
$ heroku create
$ git push heroku master
$ heroku run python manage.py migrate
$ heroku open
```

## Security

Monzo Coffee aims to be secure by default. It uses SSL throughout and is password-protected out of the box.

It is not possible to move money through the Monzo API (other than into and out of pots).

Please do not open a GitHub issue for security-related matters. You can use this [contact form](https://fncontact.com/monzo-coffee) to get in touch with the author.

## Documentation

For more information, please consult the [documentation](https://monzo-coffee.readthedocs.io/en/latest/).

