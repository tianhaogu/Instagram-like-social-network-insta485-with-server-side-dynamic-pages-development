"""
Insta485 followers view.

URLs include:
/
"""
from flask import (render_template, redirect, session, url_for, abort)
import insta485


@insta485.app.route('/users/<user_url_slug>/followers/', methods=["GET"])
def show_followers(user_url_slug):
    """Display / route."""
    # Check session
    logname = session.get("logname", "notloggedin")
    if logname == "notloggedin" or logname is None:
        return redirect(url_for("show_account_login"))

    # Connect to database
    connection = insta485.model.get_db()

    # Query whether the user is exists
    user_result = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username=?",
        [user_url_slug]
    )
    if not user_result.fetchall():
        abort(404)

    # Query the followers of user_url_slug
    cur = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2=?",
        [user_url_slug]
    )
    follower_users = cur.fetchall()
    for follower_user in follower_users:
        follower_user['username'] = follower_user['username1']

        # Query owner_img_url
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username=?",
            [follower_user['username']]
        )
        follower_user['user_img_url'] = '/uploads/' + \
            cur.fetchone()['filename']

        # Query logname_follows_username
        cur = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1=? AND username2=?",
            [logname, follower_user['username']]
        )
        if cur.fetchone():
            follower_user['logname_follows_username'] = True
        else:
            follower_user['logname_follows_username'] = False
    # insta485.app.logger.debug(follower_users)
    context = {"logname": logname,
               'followers': follower_users, "username": user_url_slug}
    return render_template("followers.html", **context)
