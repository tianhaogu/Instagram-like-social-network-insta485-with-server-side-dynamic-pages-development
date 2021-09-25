"""
Insta485 accounts view.

URLs include:
/
"""
import pathlib
import os
import uuid
import hashlib
import insta485
from flask import (flash, redirect, render_template,
                   request, session, url_for, abort)


@insta485.app.route('/accounts/login/', methods=["GET"])
def show_account_login():
    logname = session.get("logname", "notloggedin")
    if logname == "notloggedin" or logname is None:
        return render_template("login.html")
    else:
        return redirect(url_for("show_index"))


@insta485.app.route('/accounts/logout/', methods=["POST"])
def operate_account_logout():
    logname = session.get('logname')
    if logname:
        session.clear()
    return redirect(url_for('show_account_login'))


@insta485.app.route('/accounts/create/', methods=["GET"])
def show_account_create():
    logname = session.get("logname", "notloggedin")
    if logname != "notloggedin":
        return redirect(url_for("show_account_edit"))

    create_context = {"logname": logname}
    return render_template("create.html", **create_context)


@insta485.app.route("/accounts/delete/", methods=["GET"])
def show_account_delete():
    logname = session.get('logname')
    if logname is None:
        return redirect(url_for('show_login'))

    context = {"logname": logname}
    return render_template("delete.html", **context)


@insta485.app.route('/accounts/edit/', methods=["GET"])
def show_account_edit():
    logname = session.get("logname", "notloggedin")
    if logname == "notloggedin" or logname is None:
        return redirect(url_for(show_account_login))
    connection = insta485.model.get_db()

    user_result = connection.execute(
        "SELECT username, fullname, email, filename "
        "FROM users WHERE username = ?", (logname,)
    )
    curr_user = user_result.fetchone()

    users_context = {"curr_user": curr_user}
    return render_template("edit.html", **users_context)


@insta485.app.route('/accounts/password/', methods=["GET"])
def show_account_password():
    logname = session.get("logname", "notloggedin")
    if logname == "notloggedin" or logname is None:
        return redirect(url_for("show_login"))

    return render_template("password.html")


@insta485.app.route('/accounts/', methods=["POST"])
def operate_accounts():
    operation = request.form['operation']
    connection = insta485.model.get_db()
    if operation == 'login':
        logname = request.form['username']
        password = request.form['password']
        if not logname:
            abort(400)
        if not password:
            abort(400)
        insta485.app.logger.error(logname + ' ' + password)

        # Query database
        cur = connection.execute(
            "SELECT password "
            "FROM users "
            "WHERE username=?",
            [logname]
        )
        password_db = cur.fetchone()
        if not password_db:
            return abort(403)
        (algorithm, salt,
            password_hash_db) = password_db['password'].split('$')
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        if not password_hash == password_hash_db:
            return abort(403)
        session['logname'] = logname
        return redirect(url_for('show_index'))

    elif operation == "create":
        username = request.form.get("username")
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        fileobj = request.files.get("file")
        if (username is None or password is None or fullname is None
                or email is None or fileobj is None):
            flask.abort(400)

        user_search = connection.execute(
            "SELECT username FROM users "
            "WHERE username = ?", (username,)
        )
        if user_search.fetchone() is not None:
            flask.abort(409)

        filename = fileobj.filename
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(filename).suffix
        )
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])
        print(password_db_string)

        connection.execute(
            "INSERT INTO users(username, fullname, email, filename, password)"
            " VALUES (?, ?, ?, ?, ?)",
            (username, fullname, email, filename, password_db_string)
        )

        session["logname"] = username
        if request.args.get("target") is None:
            return redirect(url_for("show_index"))
        else:
            return redirect(request.args.get("target"))

    elif operation == "delete":
        logname = session.get('logname')
        if logname is None:
            return abort(403)

        user_result = connection.execute(
            "SELECT username, filename FROM users "
            "WHERE username = ?", (logname,)
        )
        curr_user = user_result.fetchone()
        ufilename = insta485.app.config["UPLOAD_FOLDER"]/curr_user["filename"]
        with open(ufilename, 'r') as handle_ufile:
            os.remove(ufilename)

        user_post_result = connection.execute(
            "SELECT owner, filename FROM posts "
            "WHERE owner = ?", (logname,)
        )
        curr_posts = user_post_result.fetchall()
        for curr_post in curr_posts:
            pfilename = insta485.app.config["UPLOAD_FOLDER"]/\
                        curr_post["filename"]
            with open(pfilename, 'r') as handle_pfile:
                os.remove(pfilename)

        connection.execute(
            "DELETE FROM users WHERE username = ?", (logname,)
        )

        session.clear()
        target_url = request.args.get("target")
        if target_url:
            return redirect(target_url)
        else:
            return redirect(url_for('show_index'))
    elif operation == "update_password":
        logname = session.get('logname')
        if logname is None:
            return abort(403)

    else:
        return redirect(url_for('show_account_login'))
