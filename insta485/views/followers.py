"""
Insta485 followers view.

URLs include:
/
"""

import insta485
from flask import (flash, redirect, render_template, send_from_directory,
                   request, session, url_for, abort)


@insta485.app.route('/users/<user_url_slug>/followers/', methods=["GET"])
def show_user_followers(user_url_slug):
    # Check Session
    logname = session.get("logname", "notloggedin")
    if logname == "notloggedin" or logname is None:
        return redirect(url_for("show_account_login"))

    # Connect to database
    connection = insta485.model.get_db()

    # Data Dict
    context = {'logname': logname}

    # Query whether the user is exists
    user_result = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username=?",
        [user_url_slug]
    )
    if not user_result.fetchall():
        abort(404)

    # Query
    follow_result = connection.execute(
        "SELECT F.username1, F.username2, U.filename "
        "FROM following F JOIN users U ON F.username1 = U.username "
        "WHERE F.username2 = ?", (user_url_slug,)
    )
    follows = follow_result.fetchall()

    all_follow_result = connection.execute(
        "SELECT username1, username2 FROM following"
    )
    all_follows = all_follow_result.fetchall()

    context = {
        "logname": logname, "imgname": curr_img, "follows_list": follows,
        "all_follows_list": all_follows
    }
    insta485.app.logger.debug(context)
    return render_template("followers.html", **context)
