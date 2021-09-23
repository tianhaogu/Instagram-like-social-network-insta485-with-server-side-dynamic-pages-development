import insta485
import uuid
import hashlib
from flask import (flash, redirect, render_template,
                   request, session, url_for, abort)


@insta485.app.route('/accounts/', methods=["POST"])
def operate_accounts():
    operation = request.form['operation']
    if operation == 'login':
        logname = request.form['username']
        password = request.form['password']
        if not logname:
            abort(400)
        if not password:
            abort(400)
        insta485.app.logger.error(logname + ' ' + password)
        # Connect to database
        connection = insta485.model.get_db()

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
    else:
        return redirect(url_for('show_login'))


@insta485.app.route('/accounts/login/')
def show_login():
    logname = session.get('logname')
    if logname is None:
        return render_template("login.html")
    else:
        return redirect(url_for('show_index'))


@insta485.app.route('/accounts/logout/', methods=["POST"])
def operate_logout():
    logname = session.get('logname')
    if logname:
        session.pop('logname')
    return redirect(url_for('show_login'))


@insta485.app.route("/accounts/delete/")
def show_delete():
    logname = session.get('logname')
    if logname is None:
        return redirect(url_for('show_login'))
    context = {"logname": logname}
    return render_template("delete.html", **context)
