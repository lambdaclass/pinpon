# pinpon

Requires [pipenv](https://github.com/pypa/pipenv/).

Setup the project and create a superuser:

    $ make init migrate superuser

Run the development server:

    $ make server

Access the admin at http://127.0.0.1:8000/admin/

## Slack commands

To use the slack integration, create a Slack applications and point a slash
command to the `/slack/` endpoint of the application.

* `/pinpon ranking`: return the current player rankings.
* `/pinpon h2h user1 user2`: return the head to head stats of two users.

![rank](rank.png)
