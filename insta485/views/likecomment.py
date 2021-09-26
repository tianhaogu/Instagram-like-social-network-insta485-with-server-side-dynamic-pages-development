"""
Insta485 like and comment operation.

URLs include:
/
"""
import flask
from flask import request
import insta485


@insta485.app.route('/likes/', methods=["POST"])
def operate_like():
    """Post Operate Like."""
    logname = flask.session["logname"]
    operation_value = request.form["operation"]
    postid_value = request.form["postid"]
    connection = insta485.model.get_db()

    like_result = connection.execute(
        "SELECT owner FROM likes WHERE postid = ?", (postid_value,)
    )
    likes = like_result.fetchall()

    if operation_value == "like":
        if {"owner": logname} in likes:
            flask.abort(409)
        connection.execute(
            "INSERT INTO likes(owner, postid) VALUES "
            "(?, ?)", (logname, postid_value,)
        )
    elif operation_value == "unlike":
        if {"owner": logname} not in likes:
            # insta485.app.logger.debug(likes)
            flask.abort(409)
        connection.execute(
            "DELETE FROM likes WHERE postid = ? AND owner = ?",
            (postid_value, logname,)
        )
    else:
        pass
    # if (request.args.get("target", "notarget") == "notarget"
    #        or request.args["target"] is None):
    if request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(request.args.get("target"))


@insta485.app.route('/comments/', methods=["POST"])
def operate_comment():
    """Post Operate Comment."""
    logname = flask.session["logname"]
    operation_value = request.form["operation"]
    postid_value = request.form.get("postid", "no_postid")
    comment_value = request.form.get("commentid", "no_commentid")
    text_value = request.form.get("text", "no_text")
    connection = insta485.model.get_db()

    comment_result = connection.execute(
        "SELECT owner FROM comments WHERE commentid = ?", (comment_value,)
    )
    curr_comment = comment_result.fetchone()

    if operation_value == "create":
        if text_value in ('', 'no_text'):
            flask.abort(400)
        connection.execute(
            "INSERT INTO comments(owner, postid, text) VALUES "
            "(?, ?, ?)", (logname, postid_value, text_value,)
        )
    elif operation_value == "delete":
        if curr_comment["owner"] != logname:
            flask.abort(400)
        connection.execute(
            "DELETE FROM comments WHERE commentid = ?", (comment_value,)
        )
    else:
        pass

    # if (request.args.get("target", "notarget") == "notarget"
    #        or request.args["target"] is None):
    if request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(request.args.get("target"))
