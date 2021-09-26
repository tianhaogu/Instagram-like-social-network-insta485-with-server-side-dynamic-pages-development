"""
Insta485 accounts view.

URLs include:
/
"""
import pathlib
import os
import uuid
import hashlib
from flask import (redirect, render_template,
                   request, session, url_for, abort)
import insta485


@insta485.app.route('/accounts/login/', methods=["GET"])
def show_account_login():
    """Get account login."""
    logname = session.get("logname", "notloggedin")
    if logname == "notloggedin" or logname is None:
        return render_template("login.html")
    return redirect(url_for("show_index"))


@insta485.app.route('/accounts/logout/', methods=["POST"])
def operate_account_logout():
    """Post account logout."""
    logname = session.get('logname')
    if logname:
        session.clear()
    return redirect(url_for('show_account_login'))


@insta485.app.route('/accounts/create/', methods=["GET"])
def show_account_create():
    """Get account create."""
    logname = session.get("logname")
    if logname is not None:
        return redirect(url_for("show_account_edit"))

    create_context = {"logname": logname}
    return render_template("create.html", **create_context)


@insta485.app.route("/accounts/delete/", methods=["GET"])
def show_account_delete():
    """Get account delete."""
    logname = session.get('logname')
    if logname is None:
        return redirect(url_for('show_account_login'))

    context = {"logname": logname}
    return render_template("delete.html", **context)


@insta485.app.route('/accounts/edit/', methods=["GET"])
def show_account_edit():
    """Get account edit."""
    logname = session.get("logname", "notloggedin")
    if logname == "notloggedin" or logname is None:
        return redirect(url_for(show_account_login))
    connection = insta485.model.get_db()

    user_result = connection.execute(
        "SELECT username, fullname, email, filename "
        "FROM users WHERE username = ?", (logname,)
    )
    curr_user = user_result.fetchone()
    curr_user['filename'] = '/uploads/' + curr_user['filename']

    users_context = {"logname": logname, "curr_user": curr_user}
    return render_template("edit.html", **users_context)


@insta485.app.route('/accounts/password/', methods=["GET"])
def show_account_password():
    """Get account password."""
    logname = session.get("logname", "notloggedin")
    if logname == "notloggedin" or logname is None:
        return redirect(url_for("show_account_login"))

    user_context = {"logname": logname}
    return render_template("password.html", **user_context)


def login_operation(connection):
    """Post account login."""
    logname = request.form['username']
    password = request.form['password']
    if not logname or not password:
        abort(400)

    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username=?",
        [logname]
    )
    password_db = cur.fetchone()
    if not password_db:
        abort(403)

    # Check the password
    (algorithm, salt,
        password_hash_db) = password_db['password'].split('$')
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()

    if not password_hash == password_hash_db:
        abort(403)
    session['logname'] = logname


def create_operation(connection):
    """Post account create."""
    username = request.form.get("username")
    password = request.form.get("password")
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    fileobj = request.files.get("file")
    if (username is None or password is None or fullname is None
            or email is None or fileobj is None):
        abort(400)
    if fileobj.filename == '':
        abort(400)

    user_search = connection.execute(
        "SELECT username FROM users "
        "WHERE username = ?", (username,)
    )
    if user_search.fetchone() is not None:
        abort(409)

    filename = fileobj.filename
    uuid_basename = "{stem}{suffix}".format(
        stem=uuid.uuid4().hex,
        suffix=pathlib.Path(filename).suffix
    )
    initial_avartar_path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(initial_avartar_path)

    # algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new('sha512')
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join(['sha512', salt, password_hash])
    print(password_db_string)

    connection.execute(
        "INSERT INTO users(username, fullname, email, filename, password)"
        " VALUES (?, ?, ?, ?, ?)",
        (username, fullname, email, uuid_basename, password_db_string)
    )
    session["logname"] = username


def delete_operation(connection):
    """Post account delete."""
    logname = session.get('logname')
    if logname is None:
        abort(403)

    user_result = connection.execute(
        "SELECT username, filename FROM users "
        "WHERE username = ?", (logname,)
    )
    curr_user = user_result.fetchone()
    ufilename = insta485.app.config["UPLOAD_FOLDER"]/curr_user["filename"]
    os.remove(ufilename)

    user_post_result = connection.execute(
        "SELECT owner, filename FROM posts "
        "WHERE owner = ?", (logname,)
    )
    curr_posts = user_post_result.fetchall()
    for curr_post in curr_posts:
        pfilename = insta485.app.config["UPLOAD_FOLDER"] /\
            curr_post["filename"]
        os.remove(pfilename)

    connection.execute(
        "DELETE FROM users WHERE username = ?", (logname,)
    )
    session.clear()


def update_password_operation(connection):
    """Post account password update."""
    logname = session.get('logname')
    if logname is None:
        abort(403)

    password = request.form.get("password")
    newpassword1 = request.form.get("new_password1")
    newpassword2 = request.form.get("new_password2")
    if not password or not newpassword1 or not newpassword2:
        abort(400)

    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username=?",
        [logname]
    )

    password_db = cur.fetchone()
    if not password_db:
        abort(403)

    # Check the password
    (algorithm, salt,
        password_hash_db) = password_db['password'].split('$')
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()

    if not password_hash == password_hash_db:
        abort(403)

    # Update newpassword
    if newpassword1 != newpassword2:
        abort(401)
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + newpassword1
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    # Update database
    connection.execute(
        "UPDATE users "
        "SET password=? "
        "WHERE username=?",
        [password_db_string, logname]
    )


def edit_account_operation(connection):
    """Post account edit."""
    # Check login
    logname = session.get('logname')
    if logname is None:
        abort(403)
    # Get data
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    fileobj = request.files.get("file")

    if not fullname or not email:
        # insta485.app.logger.debug("NO Warning!@!!!")
        abort(400)

    if fileobj is not None and fileobj.filename != '':
        # delete the file
        curl = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username=?",
            [logname]
        )
        curr_user = curl.fetchone()
        ufilename = insta485.app.config["UPLOAD_FOLDER"] / \
            curr_user["filename"]
        # insta485.app.logger.debug(str(ufilename))
        os.remove(ufilename)

        # insert new file
        filename = fileobj.filename
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(filename).suffix
        )
        avartar_path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(avartar_path)
        connection.execute(
            "UPDATE users "
            "SET filename=? "
            "WHERE username=?",
            [uuid_basename, logname]
        )
    else:
        pass

    connection.execute(
        "UPDATE users "
        "SET fullname=?, email=? "
        "WHERE username=?",
        [fullname, email, logname]
    )


@insta485.app.route('/accounts/', methods=["POST"])
def operate_accounts():
    """Post all account operations."""
    operation = request.form['operation']
    connection = insta485.model.get_db()
    if operation == 'login':
        login_operation(connection)

    elif operation == "create":
        create_operation(connection)

    elif operation == "delete":
        delete_operation(connection)

    elif operation == "update_password":
        update_password_operation(connection)

    elif operation == "edit_account":
        edit_account_operation(connection)

    else:
        pass

    if request.args.get("target") is None:
        return redirect(url_for("show_index"))
    return redirect(request.args.get("target"))
