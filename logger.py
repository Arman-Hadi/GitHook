import traceback
from datetime import datetime
from zoneinfo import ZoneInfo


line = '--------------------------------------------------'


def log_error(e, where='log.log'):
    with open(where, 'a') as f:
        tb = traceback.format_exc()
        dt = datetime.now().astimezone(tz=ZoneInfo('Asia/Tehran'))
        f.write(str(dt) + ':\n' + ''.join(tb) + '\n' + str(e) + '\n' + line)


def log(_log, where='log.log'):
    with open(where, 'a') as f:
        dt = datetime.now().astimezone(tz=ZoneInfo('Asia/Tehran'))
        f.write(
            str(dt) + ':\n' + str(_log) + '\n' + line
        )
