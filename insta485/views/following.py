"""
Insta485 following view.

URLs include:
/
"""
from flask import (redirect, render_template,
                   request, session, url_for, abort)
import insta485


@insta485.app.route('/users/<user_url_slug>/following/')
def show_following(user_url_slug):
    """Display / route."""
    # Check session
    logname = session.get("logname", "notloggedin")
    if logname is None or logname == "notloggedin":
        return redirect(url_for("show_account_login"))

    # Connect to database
    connection = insta485.model.get_db()

    # Query whether the user is exists
    user_result = connection.execute(
        "SELECT username, filename "
        "FROM users WHERE username = ?",
        (user_url_slug,)
    )
    if not user_result.fetchall():
        abort(404)

    # Query the following of user_url_slug
    cur = connection.execute(
        "SELECT username2 "
        "FROM following WHERE username1=?",
        (user_url_slug,)
    )
    # insta485.app.logger.debug(user_url_slug)
    following_users = cur.fetchall()
    for following_user in following_users:
        following_user['username'] = following_user['username2']

        # Query owner_img_url
        cur = connection.execute(
            "SELECT filename "
            "FROM users WHERE username=?",
            (following_user['username'],)
        )
        following_user['user_img_url'] = '/uploads/' + \
            cur.fetchone()['filename']

        # Query logname_follows_username
        cur = connection.execute(
            "SELECT username2 "
            "FROM following WHERE username1 = ? AND username2 = ?",
            (logname, following_user['username'],)
        )
        if cur.fetchone():
            following_user['logname_follows_username'] = True
        else:
            following_user['logname_follows_username'] = False
    # insta485.app.logger.debug(following_users)
    context = {"logname": logname, "following": following_users,
               "username": user_url_slug}
    return render_template("following.html", **context)


@insta485.app.route('/following/', methods=["POST"])
def operate_following():
    """Post Operate Following."""
    operation = request.form['operation']
    username = request.form['username']
    logname = session['logname']
    # Connect to database
    connection = insta485.model.get_db()
    curl = connection.execute(
        "SELECT * "
        "FROM following "
        "WHERE username1=? and username2=?",
        (logname, username)
    )
    # insta485.app.logger.debug(logname)
    # insta485.app.logger.debug(username)
    is_exist = curl.fetchall()
    # insta485.app.logger.debug(is_exist)
    if operation == 'follow':
        if is_exist:
            abort(409)
        else:
            connection.execute(
                "INSERT INTO following(username1, username2) VALUES "
                "(?, ?)", (logname, username,)
            )
    if operation == 'unfollow':
        if not is_exist:
            abort(409)
        else:
            connection.execute(
                "DELETE FROM following "
                "WHERE username1 = ? AND username2 = ?",
                (logname, username,)
            )

    target_url = request.args.get("target")
    if target_url:
        return redirect(target_url)
    return redirect(url_for('show_index'))
