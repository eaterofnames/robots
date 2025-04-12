"""
Robot CLI

The command line interface for the Robots tool
"""

import click
import sys
import tomllib
from robots.api.connector import RobotConnector
from robots.models import db, Robot, User, RobotAspect
from flask import Flask

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
        # Create a test user if none exists
        user = User.query.first()
        if not user:
            user = User(oauth_id='test', email='test@example.com', name='Test User')
            db.session.add(user)
            db.session.commit()
        
        # Create the robot
        robot = Robot(name=name, model=model, hostname=hostname, user_id=user.id)
        db.session.add(robot)
        db.session.commit()
        print(f"Robot '{name}' (model: {model}, hostname: {hostname}) created successfully")

@cli.command()
@click.argument('name')
def inspect(name):
    """Inspect robot details"""
    with app.app_context():
        robot = Robot.query.filter_by(name=name).first()
        if not robot:
            print(f"Error: Robot '{name}' not found")
            return
        
        print("Configuration:")
        print("  %-20s %-10s " % ("Aspect", "Value"))
        print("  %-20s %-10s " % ("------", "----"))
        for key, value in robot.to_dict().items():
            print("  %-20s %-10s" % (key, value))

@cli.command()
@click.argument('name')
def status(name):
    """Check robot status"""
    with app.app_context():
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
        
        # Get robots
        robots = query.all()
        if not robots:
            print("No robots match the specified filters")
            return
            
        # Sort if requested
        if sort:
            try:
                robots.sort(key=lambda x: getattr(x, sort, '') or '')
            except AttributeError:
                print(f"Warning: Cannot sort by '{sort}' - aspect not found")
        
        # Create header
        headers = ["Name", "Model", "Hostname", "Status", "Location"]
        if detailed:
            # Add all unique aspect names
            aspect_names = set()
            for robot in robots:
                aspect_names.update(aspect.name for aspect in robot.aspects)
            headers.extend(sorted(aspect_names))
        
        # Build rows
        rows = []
        for robot in robots:
            # Core values
            row = [
                robot.name,
                robot.model,
                robot.hostname,
                robot.status,
                robot.location
            ]
            
            # Add aspects if detailed view
            if detailed:
                robot_aspects = {a.name: a.value for a in robot.aspects}
                for aspect in headers[5:]:  # Skip core attributes
                    row.append(robot_aspects.get(aspect, '-'))
            
            rows.append(row)
        
        # Output
        print("\nRobots:")
        from tabulate import tabulate
        print(tabulate(rows, headers))

@cli.command()
@click.argument('name')
@click.option('--default', help='Default value for the aspect')
def add_aspect(name, default):
    """Add a new aspect to all robots"""
    with app.app_context():
        robots = Robot.query.all()
        if not robots:
            print("No robots registered")
            return
            
        success_count = 0
        for robot in robots:
            # Check if aspect already exists
            if not any(a.name == name for a in robot.aspects):
                aspect = RobotAspect(name=name, value=default, robot=robot)
                db.session.add(aspect)
                success_count += 1
        
        if success_count > 0:
            db.session.commit()
            print(f"Added aspect '{name}' to {success_count} robots")
            if default is not None:
                print(f"Default value set to: {default}")

@cli.command()
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def remove_aspect(name, force):
    """Remove an aspect from all robots"""
    if not force:
        if not click.confirm(f"Are you sure you want to remove the aspect '{name}'? This cannot be undone"):
            click.echo("Operation cancelled")
            return
    
    with app.app_context():
        aspects = RobotAspect.query.filter_by(name=name).all()
        if not aspects:
            print(f"Aspect '{name}' not found on any robots")
            return
        
        count = len(aspects)
        for aspect in aspects:
            db.session.delete(aspect)
        
        db.session.commit()
        print(f"Removed aspect '{name}' from {count} robots")

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