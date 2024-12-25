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
robot005  modelD   0.1.0         idle      aarch64  VN100  IDS        A100
robot006  modelE   0.1.1         idle      aarch64  VN100  IDS        A100
```

## Available Commands

### Create

`create <name> <model>` - Create a new robot with the specified name and model.

### Inspect

`inspect <name>` - Display detailed information about a robot, including its configuration and aspects.

### Status

`status <name>` - Get the current status of a robot.

### List

`list` - List all registered robots. Optional filters can be applied using the `--filter` option.

### Edit

`edit <name>` - Edit a robot's attributes, including its model, status, firmware version, and deployment status. Additional aspects can be updated using the `--aspect` option.

### Add Aspect

`add-aspect <name> [--default <value>]` - Add a new aspect to all robots. A default value can be specified using the `--default` option.

### Remove Aspect

`remove-aspect <name> [--force]` - Remove an aspect from all robots. Use the `--force` option to skip the confirmation prompt.

### Connect

`connect <name> [--command <cmd>]` - Connect to a robot via SSH using its hostname. Optionally run a command on the robot.

## Options

### Filter

`--filter <aspect> <value>` - Filter robots by a specific aspect and value. Can be used multiple times.

### Sort

`--sort <aspect>` - Sort the robot list by the specified aspect.

### Detailed

`--detailed` - Show a detailed view of robots, including all aspects.

### Aspect

`--aspect <name> <value>` - Update an aspect value for a robot.

### Force

`--force` - Skip confirmation prompts.
