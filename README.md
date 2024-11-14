## Robots 

Robots is a tool for managing a fleet of robots.

# Robots CLI

The Robots CLI is a tool for managing a fleet of robots.

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

## Options

### Filter
`--filter <aspect> <value>` - Filter robots by a specific aspect and value. Can be used multiple times.

### Detailed
`--detailed` - Show a detailed view of robots, including all aspects.

### Aspect
`--aspect <name> <value>` - Update an aspect value for a robot.

### Force
`--force` - Skip confirmation prompts.

