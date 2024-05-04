import traceback
from datetime import datetime
from zoneinfo import ZoneInfo


def log_error():
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