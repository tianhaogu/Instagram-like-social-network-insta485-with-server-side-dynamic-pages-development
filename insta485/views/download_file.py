"""Insta485 Download File."""
from flask import (session, abort, send_from_directory)
import insta485


@insta485.app.route("/uploads/<path:name>")
def download_file(name):
    """Get Download File."""
    logname = session.get('logname')
    if not logname:
        abort(403)
    return send_from_directory(
        # It will raises a 404 error automatically
        insta485.app.config['UPLOAD_FOLDER'], name, as_attachment=True
    )
