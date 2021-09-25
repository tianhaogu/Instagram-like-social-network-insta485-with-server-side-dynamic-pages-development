"""
Insta485 posts view.

URLs include:
/
"""
import flask
import arrow
import insta485
from flask import (flash, redirect, render_template,
                   request, session, url_for)


@insta485.app.route('/posts/<postid_url_slug>/', methods=["GET"])
def show_post(postid_url_slug):
    logname = flask.session.get("logname", "notloggedin")
    if logname == "notloggedin" or logname is None:
        return flask.redirect(url_for("show_account_login"))
    connection = insta485.model.get_db()

    # data dictionary
    context = {'logname': logname}

    # Query postid, owner, owner_img_url, img_url, timestamp
    post_result = connection.execute(
        "SELECT P.postid, P.filename AS Pfilename, P.owner, P.created, "
        "U.filename AS Ufilename FROM posts P JOIN users U "
        "ON P.owner = U.username WHERE P.postid = ?", (postid_url_slug,)
    )
    curr_post = post_result.fetchone()
    context['postid'] = curr_post['postid']
    context['owner'] = curr_post['owner']
    context['owner_img_url'] = '/uploads/' + curr_post['Ufilename']
    context['img_url'] = '/uploads/' + curr_post['Pfilename']
    context['timestamp'] = arrow.get(curr_post["created"]).humanize()

    # Query likes
    like_result = connection.execute(
        "SELECT P.owner AS Powner, L.owner AS Lowner "
        "FROM posts P JOIN likes L ON P.postid = L.postid "
        "WHERE P.postid = ?", (postid_url_slug,)
    )
    context['likes'] = len(like_result.fetchall())

    # Search is_logname_like
    cur = connection.execute(
        "SELECT owner "
        "FROM likes "
        "WHERE owner=? AND postid=?",
        [logname, postid_url_slug]
    )
    if cur.fetchone():
        context['is_logname_like'] = True
    else:
        context['is_logname_like'] = False

    # Query comments
    comment_result = connection.execute(
        "SELECT P.postid, C.owner, C.text, C.created, C.commentid "
        "FROM posts P JOIN comments C ON P.postid = C.postid "
        "WHERE P.postid = ? ORDER BY C.created ASC", (postid_url_slug,)
    )
    context['comments'] = comment_result.fetchall()

    return flask.render_template("post.html", **context)
