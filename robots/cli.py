"""
Robot CLI

The command line interface for the Robots tool
"""

import click
import sys
import tomllib
from robots.manager import RobotManager
from robots.connector import RobotConnector

manager = RobotManager()
config = {}
try:
    with open('robots/config/fleet-config.toml', 'rb') as f:
        config = tomllib.load(f)
except FileNotFoundError:
    print("\033[91mWarning: fleet-config.toml not found, all settings will be default\033[0m")
except Exception as e:
    print(f"\033[91mWarning: Error loading fleet-config.toml: {e}\033[0m")
    
connector = RobotConnector(config)

@click.group()
def cli():
    """Robot Fleet Management Tool"""
    pass

@cli.command()
@click.argument('name')
@click.argument('model')
@click.argument('hostname')
def create(name, model, hostname):
    """Create a new robot"""
    manager.create_robot(name, model, hostname)

@cli.command()
@click.argument('name')
def inspect(name):
    """Inspect robot details"""
    manager.inspect_robot(name)

@cli.command()
@click.argument('name')
def status(name):
    """Check robot status"""
    manager.get_robot_status(name)

@cli.command()
@click.option('--filter', '-f', multiple=True, nargs=2, help='Filter by any aspect')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed view including all aspects')
@click.option('--sort', '-s', help='Sort robots by specified aspect')
def list(filter, detailed, sort):
    """List all robots"""
    filters = {}
    if filter:
        for aspect_name, value in filter:
            if aspect_name == 'deployed':
                value = value.lower() == 'true'
            filters[aspect_name] = value
    manager.list_robots(filters, detailed=detailed, sort_by=sort)

@cli.command()
@click.argument('name')
@click.option('--model', help='Edit robot model')
@click.option('--status', help='Edit robot status')
@click.option('--hostname', help='Edit robot hostname')
@click.option('--deployed', help='Edit robot deployment status (true/false)')
@click.option('--aspect', '-a', multiple=True, nargs=2, help='Edit aspect value')
def edit(name, model, status, hostname, deployed, aspect):
    """Edit robot attributes"""
    edit_args = {
        'model': model,
        'status': status,
        'hostname': hostname,
        'deployed': deployed
    }
    if aspect:
        for aspect_name, aspect_value in aspect:
            edit_args[aspect_name] = aspect_value
    edit_args = {k: v for k, v in edit_args.items() if v is not None}
    manager.edit_robot(name, **edit_args)

@cli.command()
@click.argument('name')
@click.option('--default', help='Default value for the aspect')
def add_aspect(name, default):
    """Add a new aspect to all robots"""
    manager.add_aspect(name, default)

@cli.command()
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def remove_aspect(name, force):
    """Remove an aspect from all robots"""
    if not force:
        if not click.confirm(f"Are you sure you want to remove the aspect '{name}'? This cannot be undone"):
            click.echo("Operation cancelled")
            return
    manager.remove_aspect(name)

@cli.command()
@click.argument('name')
@click.option('--remote-command', '-c', help='Command to run on the robot')
def connect(name, remote_command):
    """Connect to a robot via SSH"""
    if name not in manager.robots:
        click.echo(f"Error: Robot '{name}' not found", err=True)
        sys.exit(1)
    robot = manager.robots[name]
    click.echo(f"Connecting to {name} via hostname:{robot.hostname}...")
    connector.connect(robot.hostname, remote_command)

@cli.command()
@click.argument('name')
@click.argument('source_dir')
@click.argument('dest_dir')
def push(name, source_dir, dest_dir):
    """Push files to a robot using rsync"""
    if name not in manager.robots:
        click.echo(f"Error: Robot '{name}' not found", err=True)
        sys.exit(1)
    robot = manager.robots[name]
    connector.transfer(robot.hostname, source_dir, dest_dir, pull=False)

@cli.command()
@click.argument('name')
@click.argument('source_dir')
@click.argument('dest_dir')
def pull(name, source_dir, dest_dir):
    """Pull files from a robot using rsync"""
    if name not in manager.robots:
        click.echo(f"Error: Robot '{name}' not found", err=True)
        sys.exit(1)
    robot = manager.robots[name]
    connector.transfer(robot.hostname, source_dir, dest_dir, pull=True)

if __name__ == '__main__':
    cli() 