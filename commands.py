import subprocess, shlex
from os import dirname
from json import loads

import logger


def configs() -> dict:
    with open(dirname(__file__) + '/configs.json', 'r') as f:
        return loads(f.read())


def run_command(cmd, cwd):
    p = subprocess.Popen(shlex.split(cmd), cwd=cwd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = p.communicate()

    if p.poll():
        error = errs if errs else outs
        logger.log(error)
        raise RuntimeError(error)

    return p, outs, errs


def git_pull(cwd, token, remote, local):
    git = configs()['git']
    return run_command(
        f"{git} pull https://{token}@github.com/{remote}.git {local}",
        cwd
    )


def docker_compose_build(cwd, service):
    docker = configs()['docker']
    return run_command(
        cwd,
        f'{docker} compose build {service}'
    )


def docker_compose_restart(cwd, service):
    docker = configs()['docker']
    down = run_command(
        cwd,
        f'{docker} compose down {service}'
    )
    up = run_command(
        cwd,
        f'{docker} compose up {service} -d'
    )
    return down, up
