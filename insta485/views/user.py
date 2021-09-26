"""
Insta485 user view.

URLs include:
/
"""
from flask import (redirect, render_template,
                   session, url_for, abort)
import insta485


@insta485.app.route('/users/<user_url_slug>/', methods=["GET"])
def show_user(user_url_slug):
    """Show User."""
    logname = session.get('logname')
    if not logname:
        return redirect(url_for('show_account_login'))
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username=?",
        [user_url_slug]
    )

    if not cur.fetchall():
        abort(404)
    context = {'logname': logname, 'username': user_url_slug}

    # Query following relationship
    cur = connection.execute(
        "SELECT * "
        "FROM following "
        "WHERE username1=? AND username2=?",
        [logname, user_url_slug]
    )
    if cur.fetchall():
        context['logname_follows_username'] = True
    else:
        context['logname_follows_username'] = False

    # Query fullname
    cur = connection.execute(
        "SELECT fullname "
        "FROM users "
        "WHERE username=?",
        [user_url_slug]
    )
    context['fullname'] = cur.fetchone()['fullname']

    # Query following
    cur = connection.execute(
        "SELECT COUNT(*) "
        "AS count "
        "FROM following "
        "WHERE username1=?",
        [user_url_slug]
    )
    context['following'] = cur.fetchone()['count']

    # Query followers
    cur = connection.execute(
        "SELECT COUNT(*) "
        "AS count "
        "FROM following "
        "WHERE username2=?",
        [user_url_slug]
    )
    context['followers'] = cur.fetchone()['count']

    # Query posts
    cur = connection.execute(
        "SELECT postid, (filename) AS img_url "
        "FROM posts "
        "WHERE owner=?",
        [user_url_slug]
    )
    context['posts'] = cur.fetchall()
    context['total_posts'] = len(context['posts'])
    for item in context['posts']:
        item['img_url'] = '/uploads/' + item['img_url']
        # insta485.app.logger.debug(item['img_url'])
    return render_template("user.html", **context)
