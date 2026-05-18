from werkzeug.exceptions import HTTPException
import tempfile
import traceback
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import pillow_heif

from backend.image_converter.infrastructure.logger import Logger
from backend.image_converter.infrastructure.cleanup_service import CleanupService
from backend.image_converter.presentation.web.routes import api_blueprint
from backend.image_converter.presentation.web.error_handlers import (
    handle_request_entity_too_large,
    handle_http_exception,
    not_found
)
from backend.image_converter.presentation.web.static_routes import static_blueprint

pillow_heif.register_heif_opener()

TEMP_DIR = tempfile.gettempdir()
EXPIRATION_TIME = 3600          

app = Flask(
    __name__,
    static_folder="static_site",
    static_url_path="/static"
)
app.config["MAX_FORM_MEMORY_SIZE"] = None
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # CH: 100 MB upload cap (was 40 GB upstream)

                            
app_logger = Logger(debug=False, json_output=False)

                                                
app.register_blueprint(api_blueprint, url_prefix="/api")
app.register_blueprint(static_blueprint, url_prefix="/")

                                     
                                     
                                     
app.register_error_handler(413, handle_request_entity_too_large)
app.register_error_handler(404, not_found)
app.register_error_handler(400, handle_http_exception)
app.register_error_handler(401, handle_http_exception)
app.register_error_handler(403, handle_http_exception)
app.register_error_handler(405, handle_http_exception)
app.register_error_handler(500, handle_http_exception)

                                      
@app.errorhandler(Exception)
def global_handle_exception(e):
    if isinstance(e, HTTPException):
        return handle_http_exception(e)

    response = {
        "error": type(e).__name__,
        "message": str(e),
        "stacktrace": traceback.format_exc()
    }
                                         
    app_logger.log(f"Exception occurred: {traceback.format_exc()}", "error")
    return jsonify(response), 500

def start_scheduler():
    """
    Start a background job to periodically clean up old temp folders.
    Uses the result pattern from CleanupService to log any errors.
    """
    cleanup_service = CleanupService(TEMP_DIR, EXPIRATION_TIME, app_logger)

    def scheduled_cleanup():
                                                          
        result = cleanup_service.cleanup_temp_folders()
        if not result.is_successful:
            app_logger.log(f"Cleanup error: {result.error}", "error")
        else:
            app_logger.log("Scheduled cleanup completed successfully.", "info")

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=scheduled_cleanup,
        trigger="interval",
        seconds=EXPIRATION_TIME
    )
    scheduler.start()
    app_logger.log("Scheduler started for periodic temp folder cleanup.", "info")


# CH: strip /image-pro prefix so existing Flask routes serve at root.
# Match only at a path boundary — startswith("/image-pro") alone would
# also match "/image-prowhatever".
class _StripImageProPrefix:
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path == "/image-pro" or path.startswith("/image-pro/"):
            environ["PATH_INFO"] = path[len("/image-pro"):] or "/"
            environ["SCRIPT_NAME"] = (environ.get("SCRIPT_NAME") or "") + "/image-pro"
        return self.app(environ, start_response)
app.wsgi_app = _StripImageProPrefix(app.wsgi_app)

# CH patches: privacy hook + temp cleanup scheduler (normally launched by bootstraper)
import os  # noqa: E402
from backend.image_converter.presentation.web import ch_privacy  # noqa: E402
ch_privacy.register(app)

# Start the upstream cleanup scheduler at WSGI import time (Gunicorn skips bootstraper).
# With Gunicorn --preload, this runs once in the master process before forking
# workers — avoiding duplicate schedulers racing on the same temp dir.
if os.environ.get("CH_DISABLE_UPSTREAM_SCHEDULER") != "1":
    try:
        start_scheduler()
    except Exception as _exc:  # noqa: BLE001
        app_logger.log(f"Could not start upstream scheduler: {_exc}", "error")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
