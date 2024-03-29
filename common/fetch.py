def fetch_backend(route, flask_request=None, method='GET'):
    from flask import current_app
    from werkzeug.exceptions import HTTPException

    import requests

    url = f"http://backend:5000{route}"

    current_app.logger.info(f"requesting backend url: {url}")

    if flask_request:
        res = requests.request(method, url, params=flask_request.args, data=flask_request.form, files=flask_request.files)
    else:
        res = requests.request(method, url)

    if res.status_code != 200:
        from werkzeug.exceptions import InternalServerError, NotFound

        msg = res.json().get("message", None)

        if res.status_code == 404:
            raise NotFound(msg)

        raise InternalServerError(msg)

    return res
