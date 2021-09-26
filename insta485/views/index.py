"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
from flask import (redirect, session, url_for)
import arrow
import insta485


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # need to add seesion
    # ======begin=========
    # ====================
    # logname = "awdeorio"
    logname = session.get('logname')
    if logname is None:
        return redirect(url_for('show_account_login'))
    # ======end=========

    # Connect to database
    connection = insta485.model.get_db()

    # Query all the posts from database
    cur = connection.execute(
        "SELECT postid, filename, owner, created "
        "FROM posts ORDER BY postid DESC"
    )
    users = cur.fetchall()
    # Query all the following users and logname itself
    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "Where username1=?",
        [logname]
    )
    following_list = [item['username2'] for item in cur.fetchall()]
    following_set = set(following_list)
    following_set.add(logname)
    users = [item for item in users if item['owner'] in following_set]

    for user in users:
        time = arrow.get(user['created'], 'YYYY-MM-DD HH:mm:ss')
        user['timestamp'] = time.humanize()
        # Query likes
        cur = connection.execute(
            "SELECT COUNT(owner) "
            "AS output "
            "FROM likes "
            "WHERE postid=?",
            [user['postid']]
        )
        user['likes'] = cur.fetchone()['output']

        # Query owner_img_url
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username=?",
            [user['owner']]
        )
        user['owner_img_url'] = '/uploads/' + cur.fetchone()['filename']
        # Query comments
        cur = connection.execute(
            "SELECT owner, text "
            "FROM comments "
            "WHERE postid=?",
            [user['postid']]
        )
        user['comments'] = cur.fetchall()
        # Change the name of file
        user['img_url'] = '/uploads/' + user['filename']

        # Search is_logname_like
        cur = connection.execute(
            "SELECT owner "
            "FROM likes "
            "WHERE owner=? AND postid=?",
            [logname, user['postid']]
        )
        if cur.fetchone():
            user['is_logname_like'] = True
        else:
            user['is_logname_like'] = False
        # insta485.app.logger.debug(cur.fetchone())

    # Add database info to context
    context = {"logname": logname, 'posts': users}
    return flask.render_template("index.html", **context)
