import traceback, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo

from sms_ir import SmsIr


line = '--------------------------------------------------'


def log_error(e, where='log.log', sms=True):
    if isinstance(e, bytes):
        e = e.decode("utf-8")
    with open(where, 'a') as f:
        tb = traceback.format_exc()
        dt = datetime.now().astimezone(tz=ZoneInfo('Asia/Tehran'))
        f.write(str(dt) + ':\n' + ''.join(tb) + '\n' + str(e) + '\n' + line)

    if sms:
        exc_type, exc_value, exc_tb = sys.exc_info()
        if exc_type:
            short_msg = f"{exc_type.__name__}: {exc_value}"
        else:
            short_msg = str(e)
        send_sms_log('GitHook', short_msg)


def send_sms_log(app_name: str, msg: str):
    SMS_API_KEY = os.environ.get('SMS_KEY')
    SMS_LINE_NUMBER = os.environ.get("SMS_LINE_NUMBER")
    MY_NUMBER = os.environ.get("MY_NUMBER")
    SMS_OTP_TEMPLATE = os.environ.get("SMS_OTP_TEMPLATE")

    sender = SmsIr(SMS_API_KEY, SMS_LINE_NUMBER)
    if len(msg) > 25:
        msg = msg[:25]

    try:
        res = sender.send_verify_code(
            number=MY_NUMBER,
            template_id=SMS_OTP_TEMPLATE,
            parameters=[
                {
                    'name': "app",
                    'value': app_name
                },
                {
                    "name": "log",
                    'value': msg
                }
            ]
        )
        if res.status_code != 200:
            log_error(f"Couldn't send sms log: {res.text}", sms=False)
    except:
        log_error("Couldn't send sms log", sms=False)
