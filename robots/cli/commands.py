"""
Robot CLI

The command line interface for the Robots tool
"""

import click
import sys
import tomllib
from tabulate import tabulate
from robots.api.connector import RobotConnector
from robots.models import db, Robot, User, RobotAspect
from flask import Flask
from sqlalchemy.exc import OperationalError
from contextlib import contextmanager

@contextmanager
def handle_db_connection():
    """Context manager to handle database connection errors gracefully."""
    try:
        yield
    except OperationalError as e:
        if "connection to server" in str(e):
            click.echo("\033[91mError: Failed to connect to the Robots database.\033[0m")
            click.echo("Please ensure the database is running and accessible.")
            click.echo(f"Connection details: {app.config['SQLALCHEMY_DATABASE_URI']}")
            sys.exit(1)
        raise

# Create a minimal Flask app for database operations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://robots:robots@localhost:5432/robots'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Load configuration
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
    with app.app_context():
        with handle_db_connection():
            if Robot.query.filter_by(name=name).first():
                print(f"Error: Robot '{name}' already exists")
                return
            
            robot = Robot(name=name, model=model, hostname=hostname)
            db.session.add(robot)
            db.session.commit()
            print(f"Created robot '{name}'")

@cli.command()
@click.argument('name')
def inspect(name):
    """Inspect a robot's details"""
    with app.app_context():
        with handle_db_connection():
            robot = Robot.query.filter_by(name=name).first()
            if not robot:
                print(f"Error: Robot '{name}' not found")
                return
            
            print(f"\nRobot: {name}")
            print(f"Model: {robot.model}")
            print(f"Hostname: {robot.hostname}")
            print(f"Status: {robot.status}")
            print(f"Location: {robot.location}")
            print("\nAspects:")
            for aspect in robot.aspects:
                print(f"  {aspect.name}: {aspect.value}")

@cli.command()
@click.argument('name')
def status(name):
    """Check robot status"""
    with app.app_context():
        with handle_db_connection():
            robot = Robot.query.filter_by(name=name).first()
            if not robot:
                print(f"Error: Robot '{name}' not found")
                return
            
            print(f"\nRobot: {name}")
            print(f"Status: {robot.status}")
            print(f"Location: {robot.location}")

@cli.command()
@click.option('--filter', '-f', multiple=True, nargs=2, help='Filter by any aspect')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed view including all aspects')
@click.option('--sort', '-s', help='Sort robots by specified aspect')
def list(filter, detailed, sort):
    """List all robots"""
    with app.app_context():
        with handle_db_connection():
            query = Robot.query
            
            # Apply filters
            if filter:
                for aspect_name, value in filter:
                    if aspect_name == 'deployed':
                        value = value.lower() == 'true'
                    if hasattr(Robot, aspect_name):
                        query = query.filter(getattr(Robot, aspect_name) == value)
                    else:
                        query = query.join(RobotAspect).filter(
                            RobotAspect.name == aspect_name,
                            RobotAspect.value == value
                        )
            
            # Apply sorting
            if sort:
                if hasattr(Robot, sort):
                    query = query.order_by(getattr(Robot, sort))
                else:
                    query = query.join(RobotAspect).filter(
                        RobotAspect.name == sort
                    ).order_by(RobotAspect.value)
            
            robots = query.all()
            
            if not robots:
                print("No robots found.")
                return
            
            # Print results using tabulate
            if not detailed:
                headers = ["Robot", "Model", "Status", "Location"]
            else:
                headers = [
                    "Name", 
                    "Model", 
                    "Hostname",
                    "Status",
                    "Location"
                ]
                # Get all unique aspect names from all robots
                aspect_names = set()
                for robot in robots:
                    aspect_names.update(aspect.name for aspect in robot.aspects)
                headers.extend(sorted(aspect_names))
            
            table = []
            for robot in robots:
                if not detailed:
                    row = [robot.name, robot.model, robot.status, robot.location]
                else:
                    row = [
                        robot.name, 
                        robot.model, 
                        robot.hostname,
                        robot.status, 
                        robot.location
                    ]
                    # Create a dictionary of aspect name to value for easy lookup
                    aspect_dict = {aspect.name: aspect.value for aspect in robot.aspects}
                    # Add aspect values in the same order as headers
                    for aspect_name in headers[5:]:  # Skip the first 5 standard columns
                        row.append(aspect_dict.get(aspect_name, '-'))
                
                if robot.status == "online":
                        row[0] = click.style(robot.name, fg='green')
                table.append(row)
            
            if detailed:
                print("\nRobots:")
                print(tabulate(table, headers, tablefmt="simple"))
            else:
                print(tabulate(table, headers, tablefmt="simple"))

@cli.command()
@click.argument('name')
@click.option('--default', help='Default value for the aspect')
def add_aspect(name, default):
    """Add a new aspect to a robot"""
    with app.app_context():
        with handle_db_connection():
            robot = Robot.query.filter_by(name=name).first()
            if not robot:
                print(f"Error: Robot '{name}' not found")
                return
            
            aspect_name = click.prompt("Enter aspect name")
            if default:
                value = default
            else:
                value = click.prompt("Enter aspect value")
            
            aspect = RobotAspect(name=aspect_name, value=value, robot=robot)
            db.session.add(aspect)
            db.session.commit()
            print(f"Added aspect '{aspect_name}' to robot '{name}'")

@cli.command()
@click.argument('name')
@click.option('--model', help='Edit robot model')
@click.option('--status', help='Edit robot status')
@click.option('--hostname', help='Edit robot hostname')
@click.option('--deployed', help='Edit robot deployment status (true/false)')
@click.option('--location', help='Edit robot location')
@click.option('--aspect', '-a', multiple=True, nargs=2, help='Edit aspect value')
def edit(name, model, status, hostname, deployed, location, aspect):
    """Edit robot attributes"""
    with app.app_context():
        with handle_db_connection():
            robot = Robot.query.filter_by(name=name).first()
            if not robot:
                print(f"Error: Robot '{name}' not found")
                return
            
            # Edit core attributes
            if model is not None:
                robot.model = model
            if status is not None:
                robot.status = status
            if hostname is not None:
                robot.hostname = hostname
            if deployed is not None:
                robot.deployed = deployed.lower() == 'true'
            if location is not None:
                robot.location = location
            
            # Edit aspects
            if aspect:
                for aspect_name, aspect_value in aspect:
                    # Check if aspect exists
                    existing_aspect = RobotAspect.query.filter_by(
                        robot_id=robot.id,
                        name=aspect_name
                    ).first()
                    
                    if existing_aspect:
                        # Update existing aspect
                        existing_aspect.value = aspect_value
                    else:
                        # Create new aspect
                        new_aspect = RobotAspect(
                            name=aspect_name,
                            value=aspect_value,
                            robot=robot
                        )
                        db.session.add(new_aspect)
            
            db.session.commit()
            print(f"Updated robot '{name}'")

@cli.command()
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def remove_aspect(name, force):
    """Remove an aspect from a robot"""
    with app.app_context():
        with handle_db_connection():
            robot = Robot.query.filter_by(name=name).first()
            if not robot:
                print(f"Error: Robot '{name}' not found")
                return
            
            aspect_name = click.prompt("Enter aspect name to remove")
            aspect = RobotAspect.query.filter_by(
                robot_id=robot.id,
                name=aspect_name
            ).first()
            
            if not aspect:
                print(f"Error: Aspect '{aspect_name}' not found on robot '{name}'")
                return
            
            if not force:
                if not click.confirm(f"Remove aspect '{aspect_name}' from robot '{name}'?"):
                    return
            
            db.session.delete(aspect)
            db.session.commit()
            print(f"Removed aspect '{aspect_name}' from robot '{name}'")

@cli.command()
@click.argument('name')
@click.option('--remote-command', '-c', help='Command to run on the robot')
def connect(name, remote_command):
    """Connect to a robot via SSH"""
    with app.app_context():
        robot = Robot.query.filter_by(name=name).first()
        if not robot:
            click.echo(f"Error: Robot '{name}' not found", err=True)
            sys.exit(1)
        
        click.echo(f"Connecting to {name} via hostname:{robot.hostname}...")
        connector.connect(robot.hostname, remote_command)

@cli.command()
@click.argument('name')
@click.argument('source_dir')
@click.argument('dest_dir')
def push(name, source_dir, dest_dir):
    """Push files to a robot using rsync"""
    with app.app_context():
        robot = Robot.query.filter_by(name=name).first()
        if not robot:
            click.echo(f"Error: Robot '{name}' not found", err=True)
            sys.exit(1)
        
        connector.transfer(robot.hostname, source_dir, dest_dir, pull=False)

@cli.command()
@click.argument('name')
@click.argument('source_dir')
@click.argument('dest_dir')
def pull(name, source_dir, dest_dir):
    """Pull files from a robot using rsync"""
    with app.app_context():
        robot = Robot.query.filter_by(name=name).first()
        if not robot:
            click.echo(f"Error: Robot '{name}' not found", err=True)
            sys.exit(1)
        
        connector.transfer(robot.hostname, source_dir, dest_dir, pull=True)

if __name__ == '__main__':
    cli() 