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

## Installation - CLI utility

1. Clone the repository: `git clone https://github.com/eaterofnames/robots.git`
2. Get inside a venv of your choice. We're using `python -m venv robots`.
3. Change into the repo directory: `cd robots`
4. Use pip: `pip install -e .`

## Installation - Backend

The backend requires a PostgreSQL database which is provided via Docker. Here's how to set it up:

1. Make sure you have Docker and Docker Compose installed on your system.

2. The database configuration is managed through `fleet-config.toml`. The default configuration is:
   ```toml
   DATABASE_URL="postgresql://robots:robots@localhost:5432/robots"
   SQLALCHEMY_TRACK_MODIFICATIONS = "False"
   ```

3. Start the database container:
   ```shell
   docker-compose up -d
   ```

4. Verify the database is running:
   ```shell
   docker-compose ps
   ```

The database will be queryable via `robots list`. See below for more.

## Usage

`robots` is a CLI tool. It's built with `click` and `toml`. After installation, you can run `robots` to see the help menu. It relies on a database, right now that's hosted in a docker container for development.

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

## Feature List

Here's what I want to add over time:

1. Robots is multi-user. Some sort of remotely hosted fleet-config and robot database will be needed for this.
2. Robots has a web interface, preferably hosted from the same place as above.
3. Robots is logging interactions that users make.
4. Robots has an API for the robots themselves to report their status and other information.
5. Robots supports build definitions for robots, which can be used to build a deployment payload for a robot.
6. Robots supports a deployment system that can be used to deploy the above build payload to a robot.
7. Robots has a pull-based system for fetching built releases down to robots.