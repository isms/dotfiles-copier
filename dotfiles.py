#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sh
import yaml
import click
from sh import cp
from sh import git
from sh import mkdir
from datetime import datetime
import tarfile


HOME_DIR = os.environ.get('HOME')
DEFAULT_DIR = os.path.join(HOME_DIR, ".dotfiles")
DIR_PATH_TYPE = click.Path(exists=True, resolve_path=True,
    writable=True, dir_okay=True, file_okay=False)

DEFAULT_CONF = os.path.join(HOME_DIR, ".dotfiles.yml")
CONF_PATH_TYPE = click.Path(exists=True, resolve_path=True,
    readable=True, dir_okay=False, file_okay=True)


def handle_task(task, dotfiles_dir):
    click.echo('handling task: {}'.format(task))

    if 'src' not in task:
        click.echo("you must define at least a 'src' in each task")
        raise click.Abort

    source = os.path.expanduser(task['src'])
    if not os.path.exists(source):
        click.echo('file not found: {}'.format(source))
        raise click.Abort

    _, filename = os.path.split(source)
    subdir = task['subdir'].rstrip('/') if 'subdir' in task else '.'
    target = os.path.abspath(os.path.join(dotfiles_dir, subdir, filename))
    
    # make sure the target directory exists, e.g. .dotfiles/bash/
    target_path, _ = os.path.split(target)
    mkdir('-p', target_path)

    # copy the files
    msg_fmt = 'copying {}: from [{}] to [{}]'
    if os.path.isdir(source):
        click.echo(msg_fmt.format('dir', source, target))
        cp("-r", os.path.join(source, "."), target)
    else:
        click.echo(msg_fmt.format('file', source, target))
        cp(source, target)    


def check_git_repo(git_path):
    """
    make sure there's actually a git repo initialized and
    check the git-diff exit code for changes if it exists

    git-diff exit codes:
    - 0: no changes
    - 1: changes
    - 129: no git repo
    """
    os.chdir(git_path)
    changed = False
    created = False
    try:
        git("diff", "--exit-code")
    except sh.ErrorReturnCode_1:
        changed = True
    except sh.ErrorReturnCode_129:
        click.echo("no git repo found; initializing a new repo")
        git.init()
        git.add(".")
        click.echo(git.commit('-m"Initial commit"'))
        created = True
    return created, changed


def commit_changes(git_path):
    os.chdir(git_path)
    click.echo(git.add("."))
    now = datetime.now().isoformat()
    click.echo(git.commit("-a", '-m"Updated {}"'.format(now)))


@click.command()
@click.argument('conf_path', type=CONF_PATH_TYPE, default=DEFAULT_CONF)
@click.option('--dest', type=DIR_PATH_TYPE, default=None)
@click.option('--git-commit/--no-commit', default=False)
@click.option('--tar-gz')
def main(conf_path, dest, git_commit, tar_gz):
    # load the config
    with open(conf_path, 'r') as f:
        conf = yaml.safe_load(f)

    # if the dotfiles directory is defined in the config file, use that
    if dest is not None:
        click.echo("backup directory specified as argument")
        dotfiles_dir = dest
    elif 'dest' in conf:
        click.echo("backup directory specified in config file")
        dotfiles_dir = os.path.expanduser(conf['dest'])
    else:
        click.echo("backup directory not specified, using default")
        dotfiles_dir = DEFAULT_DIR
    click.echo('using directory {}'.format(dotfiles_dir))

    # copy the files
    for task in conf['tasks']:
        handle_task(task, dotfiles_dir)

    # git commit if desired and changes were made
    if git_commit:
        created, changed = check_git_repo(dotfiles_dir)

        if changed:
            click.echo('committing changes to git')
            commit_changes(dotfiles_dir)
        
        if not created and not changed:
            click.echo('no changes made, skipping git commit')
    if tar_gz is not None:
        click.echo('tar-gz file specified by argument')
        archive = tar_gz
    elif 'archive' in conf:
        click.echo('tar-gz specified in config')
        archive = os.path.expanduser(conf['archive'])
    click.echo('using archive path {}'.format(archive))

    if archive:
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(dotfiles_dir, arcname=os.path.basename(dotfiles_dir))


if __name__ == '__main__':
    main()
