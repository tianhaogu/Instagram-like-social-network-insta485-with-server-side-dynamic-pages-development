"""
Insta485 explore view.

URLs include:
/users/<user_url_slug>/
"""
import insta485
import uuid
import hashlib
from flask import (flash, redirect, render_template,
                   request, session, url_for, abort)


@insta485.app.route('/explore/', methods=["GET"])
def show_explore():
    # Session Control
    logname = session.get('logname')
    if not logname:
        redirect(url_for('show_login'))

    # Connect to database
    connection = insta485.model.get_db()

    # Query the folloing of logname
    cur = connection.execute(
        "SELECT DISTINCT username2 "
        "FROM following "
        "WHERE username1=?",
        [logname]
    )
    following_users = cur.fetchall()
    following_users_sets = set([item['username2'] for item in following_users])
    following_users_sets.add(logname)
    # Query the not following of logname
    cur = connection.execute(
        "SELECT DISTINCT username2 "
        "FROM following "
        "WHERE username1!=?",
        [logname]
    )
    not_follow_users = cur.fetchall()

    # Get the not following
    not_follow_users = [
        item for item in not_follow_users if item['username2'] not in following_users_sets]

    for not_follow_user in not_follow_users:
        not_follow_user['username'] = not_follow_user['username2']

        # Query owner_img_url
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username=?",
            [not_follow_user['username']]
        )
        not_follow_user['user_img_url'] = '/uploads/' + \
            cur.fetchone()['filename']
    context = {"logname": logname, 'not_following': not_follow_users}
    return render_template("explore.html", **context)
