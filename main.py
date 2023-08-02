from flask import Flask, request
from werkzeug.exceptions import HTTPException
import hashlib
import hmac
from datetime import datetime
import traceback
from zoneinfo import ZoneInfo


def log_error(e):
    with open('log.log', 'a') as f:
        tb = traceback.format_exc()
        dt = datetime.now().astimezone(tz=ZoneInfo('Asia/Tehran'))
        f.write(f"""{str(dt)}:
{''.join(tb)}
------------------------------------------------------------------------------

""")


def log(_log):
    with open('log.log', 'a') as f:
        dt = datetime.now().astimezone(tz=ZoneInfo('Asia/Tehran'))
        f.write(
            str(dt) + ':\n' + str(_log) + '\n'
        )


def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256.
    
    Raise and return 403 if not authorized.
    
    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        raise HTTPException(status_code=403, detail="x-hub-signature-256 header is missing!")
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")

app = Flask(__name__)


@app.route("/apihook", methods=['POST',])
def apihook():
    try:
        payload = request.get_data()
        sig_header = request.headers.get('x-hub-signature-256', '')
        verify_signature(payload, 'apihoook_aslfjasdwevn2408', sig_header)

        data = request.get_json()
        if data['repository']['full_name'] == 'BracketAcademy/BracketAcademy':
            log(data)
    except Exception as e:
        log_error(e)
        return str(e), 400

    return "<h1 style='color:blue'>Hello There!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
