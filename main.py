import hashlib, hmac
from os.path import dirname
from json import loads
from typing import List
from threading import Thread

from flask import Flask, request
from werkzeug.exceptions import HTTPException

import commands, logger


def get_configs() -> dict:
    try:
        with open(dirname(__file__) + '/configs.json', 'r') as f:
            return loads(f.read())
    except:
        raise Exception("No configs.json file found.")
    
def get_repos() -> List[dict]:
    try:
        with open(dirname(__file__) + '/repos.json', 'r') as f:
            return loads(f.read())
    except:
        raise Exception("No repos.json file found.")


def get_changes(github_data: dict):
    changes = []
    if 'commits' in github_data:
        for commit in github_data['commits']:
            changes += commit['added'] + commit['removed'] + commit['modified']
    return changes


def check_a_in_b(a: list, b: list) -> bool:
    b_string = '__'.join(b)
    for i in a:
        return i in b_string
    return False


def do_the_thing(data, repo):
    changes = get_changes(data)
    services = repo['docker_services']
    path = repo['path']

    commands.git_pull(path, repo['token'], repo['repository'], repo['local_branch'])

    if repo['always_build'] or check_a_in_b(repo['build_files'], changes):
        for service in services:
            commands.docker_compose_build(path, service)
        for service in services:
            commands.docker_compose_restart(path, service)
        return
    
    print(changes)
    print(check_a_in_b(repo['restart_files'], changes))

    if repo['always_restart'] or check_a_in_b(repo['restart_files'], changes):
        for service in services:
            commands.docker_compose_restart(path, service)


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
        verify_signature(payload, get_configs()['github_secret_token'], sig_header)

        data = request.get_json()
        for repo in get_repos():
            if data['repository']['full_name'] == repo['repository']:
                task = Thread(target=do_the_thing, args=(data, repo))
                task.start()
                return "OK"
    except Exception as e:
        logger.log_error()
        return e.__class__.__name__


@app.route("/list")
def list_hooks():
    return [repo['name'] for repo in get_repos()]


if __name__ == "__main__":
    # configs = get_configs()
    app.run(host='0.0.0.0')
