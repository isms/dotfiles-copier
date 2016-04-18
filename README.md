# dotfiles-copier

A single script to copy all of your scattered dotfiles and
config folders to a specified directory. Can automatically
`git commit` changes.

### Example

Let's say we want to keep a Github repo with our various config
files, starting with my `.bashrc`. We define a configuration in
`~/.dotfiles.yml`:

```yaml
---
dest: "~/.dotfiles"
tasks:
  - src: "~/.bashrc"
```

Then run the script with the `--git-commit` option:

```
$ dotfiles.py --git-commit
backup directory specified as argument
using directory /home/isaac/.dotfiles
handling task: {'src': '~/.bashrc'}
copying file: from [/home/isaac/.bashrc] to [/home/isaac/.dotfiles/.bashrc]
no git repo found; initializing a new repo
[master (root-commit) 153aec5] "Initial commit"
 1 file changed, 315 insertions(+)
 create mode 100644 .bashrc
```

Now let's say we change `~/.bashrc`. If we run the command again,
it will commit those changes:

```
$ dotfiles.py --git-commit
...
copying file: from [/home/isaac/.bashrc] to [/home/isaac/.dotfiles/.bashrc]
committing changes to git

[master 99f69c6] "Updated 2016-04-18T05:32:26.834969"
 1 file changed, 1 insertion(+), 1 deletion(-)
```

### Installation

1. Make sure that the requirements are installed. If you're
going to use the `--git-commit` option, you'll need git installed.

2. You'll probably want to install the Python dependencies system-wide
so that you don't need to run in a virtual environment.

3. Then just put `dotfiles.py` somewhere on your `PATH`.

### Configuration

You tell `dotfiles.py` which files to copy into your backup
directory (by default, `~/.dotfiles`) by changing the `tasks`
entry in a config file (by default, `~/.dotfiles.yml`).

Each task must have a key called `src` which is a file or
directory on your system. By default, each of these `src`
entries will be copied right into your backup directory.

If you wish to arrange the files specifically in a subdirectory
of the backup directory, you can include a `subdir` entry in
the task.

Here is an example with subdirs:

```yaml
---
dest: "~/.dotfiles"
tasks:
    # misc files from home directory
  - src: "~/.bashrc"
  - src: "~/.vimrc"
  - src: "~/.xprofile"
  
  # i3 stuff
  - src: "~/.i3"
    subdir: "i3/home"
  - src: "/etc/i3"
    subdir: "i3/etc"
  - src: "/etc/i3status.conf"
    subdir: "i3/etc"

  # system stuff
  - src: "/etc/fstab"
    subdir: "etc"
```

This config will result in the following backup folder:

`~/.dotfiles`
```
.
├── .bashrc
├── etc
│   └── fstab
├── i3
│   ├── etc
│   │   ├── i3
│   │   │   ├── config
│   │   │   └── config.keycodes
│   │   └── i3status.conf
│   └── home
│       └── .i3
│           └── config
├── .vimrc
└── .xprofile
```

### Usage

```
Usage: dotfiles.py [OPTIONS] [CONF_PATH]

Options:
  --dotfiles_dir DIRECTORY
  --git-commit / --no-commit
  --help                      Show this message and exit.
```