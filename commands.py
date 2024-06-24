from os.path import dirname
import subprocess, shlex
from json import loads

import logger


def configs() -> dict:
    with open(dirname(__file__) + '/configs.json', 'r') as f:
        return loads(f.read())


def run_command(cmd, cwd, where='log.log'):
    p = subprocess.Popen(shlex.split(cmd), cwd=cwd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = p.communicate()

    if p.poll():
        error = errs if errs else outs
        logger.log_error(error, where)
        raise RuntimeError(error)

    return p, outs, errs


def git_pull(cwd, token, remote, local, **kwargs):
    git = configs()['git']
    return run_command(
        f"{git} pull https://{token}@github.com/{remote}.git {local}",
        cwd, **kwargs
    )


def docker_compose_build(cwd, service, **kwargs):
    docker = configs()['docker']
    
    build = run_command(
        f'{docker} compose build {service} --no-cache',
        cwd, **kwargs
    )
    prune = run_command(
        f'{docker} builder prune -a -f',
        cwd, **kwargs
    )
    return build, prune


def docker_compose_restart(cwd, service, **kwargs):
    docker = configs()['docker']
    down = run_command(
        f'{docker} compose down {service}',
        cwd, **kwargs
    )
    up = run_command(
        f'{docker} compose up {service} -d',
        cwd, **kwargs
    )
    return down, up
