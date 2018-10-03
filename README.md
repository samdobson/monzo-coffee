# :credit_card: Monzo Coffee :coffee:

Bulk tag historical transactions using your own custom rules.

Group your `#coffee` spending and make it searchable/filterable in the Monzo app.

Powered by [monzo-python](https://github.com/samdobson/monzo-python).

## :computer: One-click deployment

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

You will be prompted for a *Monzo Access Token* which can be obtained via the [Monzo Developer Portal](https://developers.monzo.com)

Check the configuration variables for your password.

Step-by-step instructions can be found in the [quickstart guide](https://monzo-coffee.readthedocs.io/en/latest/quickstart.html).

## :wrench: Development

You will need to have installed:

* [Python 3.6](http://install.python-guide.org)
* [pipenv](https://pipenv.readthedocs.io/en/latest/)
* [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

```sh
$ git clone https://github.com/samdobson/monzo-coffee
$ cd monzo-coffee

$ pipenv install

$ python manage.py migrate
$ python manage.py collectstatic

$ heroku local
```
Your app is now accessible on [localhost:5000](http://localhost:5000/).

To deploy to Heroku:

```sh
$ heroku create
$ git push heroku master
$ heroku run python manage.py migrate
$ heroku open
```

## :lock: Security

Monzo Coffee aims to be secure by default. It uses SSL throughout and is password-protected out of the box.

The Monzo API does not allow movement of money (other than into/out of pots). Access tokens expire after 4 hours.

You should not allow other people to use your app. Point them to this repo and have them deploy their own instance.

Please do not open a GitHub issue for security-related matters - use this [contact form](https://fncontact.com/monzo-coffee) to contact the author.

## :green_book: Documentation

For more information, please consult the [documentation](https://monzo-coffee.readthedocs.io/en/latest/).

Support is provided on a best-efforts basis.
