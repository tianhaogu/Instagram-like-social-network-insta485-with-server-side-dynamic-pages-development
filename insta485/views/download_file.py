import insta485
from flask import (flash, redirect, render_template,
                   request, session, url_for, abort, send_from_directory)


@insta485.app.route("/uploads/<path:name>")
def download_file(name):
    logname = session.get('logname')
    if not logname:
        abort(403)
    return send_from_directory(
        # It will raises a 404 error automatically
        insta485.app.config['UPLOAD_FOLDER'], name, as_attachment=True
    )
