from flask import Flask, request
from werkzeug.exceptions import HTTPException
import hashlib
import hmac
from datetime import datetime
import traceback
from zoneinfo import ZoneInfo
import subprocess
from shlex import split


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
    

def run_command(cmd, cwd):
    p = subprocess.Popen(split(cmd), cwd=cwd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = p.communicate()

    if p.poll():
        error = errs if errs else outs
        log(error)
        raise RuntimeError(error)

    return p, outs, errs


app = Flask(__name__)

@app.route("/apihook", methods=['POST',])
def apihook():
    try:
        payload = request.get_data()
        sig_header = request.headers.get('x-hub-signature-256', '')
        verify_signature(payload, 'apihoook_aslfjasdwevn2408', sig_header)

        data = request.get_json()
        if data['repository']['full_name'] == 'BracketAcademy/BracketAcademy':
            cwd = '/root/w/Bracket/backend'
            run_command('git pull https://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@github.com/BracketAcademy/BracketAcademy.git main', cwd)
            run_command("docker compose down", cwd)
            run_command("docker compose up -d", cwd)
            return 'OK BRACKET'
        elif data['repository']['full_name'] == 'BracketAcademy/feedlink':
            log('--------------into if --------------------')
            cwd = '/root/w/FeedLink/front'
            run_command('git pull https://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@github.com/BracketAcademy/feedlink.git master', cwd)
            return 'OK FEEDLINK'
    except Exception as e:
        log_error(e)
        return str(e), 400

    return "OK KAKA"


@app.route("/list")
def list_hooks():
    return ['bracket', 'feedlink']


if __name__ == "__main__":
    app.run(host='0.0.0.0')
