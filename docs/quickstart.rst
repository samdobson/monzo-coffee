:github_url: https://github.com/samdobson/monzo-coffee/edit/master/docs/index.rst

Quickstart
==========

Monzo Coffee is a web app for tagging your Monzo transactions.

It uses the Monzo API to fetch your transaction data, and allows you to tag your transactions however you want.

You will need to deploy your own version of the app to use it.

You can do this with one click with Heroku. Heroku is a cloud platform for rapid deployment of applications. You will need a free account to get started.

.. image:: https://www.herokucdn.com/deploy/button.svg
   :target: https://heroku.com/deploy/?template=https://github.com/samdobson/monzo-coffee

In order to use this app, you will need a Monzo API Access Token. You can get one through the `Monzo Developers Portal <https://developers.monzo.com>`. You sign in using the same email address as your Monzo account. You will need to click the link in your email to gain access to the portal. Once you are in, copy the Access Token. You will need it in a moment.

.. note::
   Your access token will expire after a few hours. Once it expires,
   you will need to get a new one.

Use the deploy button above. Choose any app name and region you like. Paste your Access Token into the appropriate field and hit `Deploy`.

.. note::
   Go brew yourself a coffee. The app deployment will take a few minutes.

Hit `Manage App` and navigate to the `Settings` tab. Click the `Reveal Config Vars` button and copy the `PASSWORD`. Click `Open App` and paste the password. You're in!

Usage
-----

Select the account you wish to use from the dropdown.

There are a few preset tags to play with. Hitting `Month Short`, for example, will add a `#sep` tag to all of your transactions in September. If you open the Monzo app on your phone, you will now be able to search `#sep` and see all of your spending for September.

Custom tags are defined using Python code. A handful of examples have been created for you as a demonstration. Feel free to modify these or use them as a template to meet your own tagging needs.

Enjoy!

