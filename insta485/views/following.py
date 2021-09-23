"""
Insta485 following view.

URLs include:
/
"""
import flask
import arrow
import insta485
import functools
from flask import (flash, redirect, render_template,
                   request, session, url_for, abort)


@insta485.app.route('/users/<user_url_slug>/following/')
def show_following(user_url_slug):
    """Display / route."""

    # need to add seesion
    # ======begin=========
    # ====================
    logname = "awdeorio"
    # ======end=========

    # Connect to database
    connection = insta485.model.get_db()

    # Query the following of user_url_slug
    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1=?",
        [user_url_slug]
    )
    insta485.app.logger.debug(user_url_slug)
    following_users = cur.fetchall()
    if not following_users:
        abort(404)
    insta485.app.logger.debug(following_users)
    for following_user in following_users:
        following_user['username'] = following_user['username2']

        # Query owner_img_url
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username=?",
            [following_user['username']]
        )
        following_user['user_img_url'] = '/uploads/' + \
            cur.fetchone()['filename']

        # Query logname_follows_username
        cur = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1=? AND username2=?",
            [logname, following_user['username']]
        )
        if cur.fetchone():
            following_user['logname_follows_username'] = True
        else:
            following_user['logname_follows_username'] = False
    insta485.app.logger.debug(following_users)
    context = {"logname": logname, 'following': following_users}
    return flask.render_template("following.html", **context)
