# Robots CLI

The Robots CLI is a tool for managing a fleet of robots.

```shell
$ ./robot_cli.py list --detailed

Robots:
Name      Model    Hostname      Status    CPU      IMU    cameras    gpu
--------  -------  ------------  --------  -------  -----  ---------  -----
robot001  modelA   stonks.local  DEV       aarch64  VN100  IDS        A100
robot002  modelA   0.1.0         idle      aarch64  VN100  IDS        A100
robot003  modelB   0.1.1         idle      aarch64  VN100  IDS        A100
robot004  modelC   0.1.2         idle      aarch64  VN100  IDS        A100
```

## What is it?

`robots` at its core is an abstraction of linux commands coupled with a table of robots. A fleet manager may find themselves performing these actions:

- Create a new robot entry (can also be thought of as 'registering' the robot).
- Add aspects to robots, such as a camera model, firmware version, GPU, etc.
- Edit a robots aspects as upgrades or component replacements occur.
- Connect to a robot and run a command on it.
- Transfer files between a robot and the local machine.
- Get the status of a robot.

`robots` aims to make these faster, and allow lower-level robot managers to be abstracted away from the robot users.

## Installation

1. Clone the repository: `git clone https://github.com/eaterofnames/robots.git`
2. Get inside a venv of your choice. We're using `python -m venv robots`.
3. Change into the repo directory: `cd robots`
4. Use pip: `pip install -e .`

## Usage

`robots` is a CLI tool. It's built with `click` and `toml`. After installation, you can run `robots` to see the help menu.

Some basic commands to get you started:

```shell
$ robots list
$ robots create robot001 modelA stonks.local
$ robots edit robot001 model=modelB status=idle
$ robots connect robot001
$ robots push robot001 /path/to/local/dir /path/to/robot/dir
```

## Configuration

`robots` uses a `fleet-config.toml` file to store fleet-wide configuration settings, such as ssh and rsync options.
