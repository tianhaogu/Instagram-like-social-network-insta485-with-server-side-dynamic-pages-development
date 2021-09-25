"""
Insta485 posts view.

URLs include:
/
"""
import flask
import os
import arrow
import uuid
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


@insta485.app.route('/posts/', methods=["POST"])
def operate_post():
    logname = flask.session["logname"]
    operation_value = request.form["operation"]
    connection = insta485.model.get_db()

    if operation_value == "delete":
        postid_value = request.form["postid"]

        post_result = connection.execute(
            "SELECT postid, owner, filename FROM posts "
            "WHERE postid = ?", (postid_value,)
        )
        curr_post = post_result.fetchone()

        path = insta485.app.config["UPLOAD_FOLDER"]/curr_post["filename"]
        with open(path, 'r') as handle_file:
            os.remove(path)

        if curr_post["owner"] != logname:
            flask.abort(403)
        connection.execute(
            "DELETE FROM posts WHERE postid = ?", (postid_value)
        )
    elif operation_value == "create":
        fileobj = flask.request.files["file"]
        if fileobj is None:
            flask.abort(400)
        filename = fileobj.filename

        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(filename).suffix
        )
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        connection.execute(
            "INSERT INTO posts(filename, owner) VALUES "
            "(?, ?)", (filename, logname)
        )
    else:
        pass

    if (request.args.get("target", "notarget") == "notarget" 
            or request.args.get("target") is None):
        return flask.redirect(flask.url_for('show_user', user_url_slug=logname))
    else:
        return flask.redirect(request.args.get("target"))