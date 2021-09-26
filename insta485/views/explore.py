"""
Insta485 explore view.

URLs include:
/users/<user_url_slug>/
"""
from flask import (redirect, render_template, session, url_for)
import insta485


@insta485.app.route('/explore/', methods=["GET"])
def show_explore():
    """Get Show Explore."""
    # Session Control
    logname = session.get('logname')
    if not logname:
        redirect(url_for('show_login'))

    # Connect to database
    connection = insta485.model.get_db()

    # Query the folloing of logname
    cur = connection.execute(
        "SELECT DISTINCT username "
        "FROM users "
        "WHERE username NOT IN ( "
        "SELECT DISTINCT username2 "
        "FROM following "
        "WHERE username1=?) "
        "AND username!=?",
        [logname, logname]
    )
    explore_users = cur.fetchall()

    for explore_user in explore_users:
        # Query owner_img_url
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username=?",
            [explore_user['username']]
        )
        explore_user['user_img_url'] = '/uploads/' + \
            cur.fetchone()['filename']
    context = {"logname": logname, 'not_following': explore_users}
    return render_template("explore.html", **context)
