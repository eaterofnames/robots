#!/usr/bin/env python3
import argparse
import sys
import tomllib
from robot_manager import RobotManager
from robot_connector import RobotConnector

def main():
    manager = RobotManager()
    
    # Load config from fleet-config.toml
    config = {}
    try:
        with open('fleet-config.toml', 'rb') as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        print("Warning: fleet-config.toml not found, using default settings")
    except Exception as e:
        print(f"Warning: Error loading fleet-config.toml: {e}")
        
    connector = RobotConnector(config)
    
    parser = argparse.ArgumentParser(description='Robot Fleet Management Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new robot')
    create_parser.add_argument('name', help='Name of the robot')
    create_parser.add_argument('model', help='Model of the robot')
    create_parser.add_argument('hostname', help='Hostname of the robot')

    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect robot details')
    inspect_parser.add_argument('name', help='Name of the robot')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check robot status')
    status_parser.add_argument('name', help='Name of the robot')
    
    # List command with filters
    list_parser = subparsers.add_parser('list', help='List all robots')
    list_parser.add_argument('--filter', '-f', action='append', nargs=2,
                           metavar=('ASPECT', 'VALUE'),
                           help='Filter by any aspect (can be used multiple times)')
    list_parser.add_argument('--detailed', '-d', action='store_true',
                            help='Show detailed view including all aspects')
    list_parser.add_argument('--sort', '-s', help='Sort robots by specified aspect')
    
    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit robot attributes')
    edit_parser.add_argument('name', help='Name of the robot')
    edit_parser.add_argument('--model', help='Update robot model')
    edit_parser.add_argument('--status', help='Update robot status')
    edit_parser.add_argument('--hostname', help='Update hostname')
    edit_parser.add_argument('--deployed', help='Update deployment status (true/false)')
    edit_parser.add_argument('--aspect', '-a', action='append', nargs=2,
                           metavar=('NAME', 'VALUE'),
                           help='Update aspect value (can be used multiple times)')
    
    # Add aspect command
    aspect_parser = subparsers.add_parser('add-aspect', help='Add a new aspect to all robots')
    aspect_parser.add_argument('name', help='Name of the aspect')
    aspect_parser.add_argument('--default', help='Default value for the aspect')
    
    # Remove aspect command
    remove_aspect_parser = subparsers.add_parser('remove-aspect', help='Remove an aspect from all robots')
    remove_aspect_parser.add_argument('name', help='Name of the aspect to remove')
    remove_aspect_parser.add_argument('--force', '-f', action='store_true', 
                                    help='Skip confirmation prompt')
    
    # Connect command
    connect_parser = subparsers.add_parser('connect', help='Connect to a robot via SSH')
    connect_parser.add_argument('name', help='Name of the robot to connect to')
    connect_parser.add_argument('--remote_command', '-c', help='Command to run on the robot')
    
    # Push command
    push_parser = subparsers.add_parser('push', help='Push files to a robot using rsync')
    push_parser.add_argument('name', help='Name of the robot')
    push_parser.add_argument('source_dir', help='Local source directory to push from')
    push_parser.add_argument('dest_dir', help='Remote destination directory on the robot')
    
    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Pull files from a robot using rsync')
    pull_parser.add_argument('name', help='Name of the robot')
    pull_parser.add_argument('source_dir', help='Remote source directory on the robot')
    pull_parser.add_argument('dest_dir', help='Local destination directory to pull to')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        manager.create_robot(args.name, args.model, args.hostname)
    elif args.command == 'inspect':
        manager.inspect_robot(args.name)
    elif args.command == 'status':
        manager.get_robot_status(args.name)
    elif args.command == 'list':
        filters = {}
        if args.filter:
            for aspect_name, value in args.filter:
                # Convert 'true'/'false' strings to booleans for deployed status
                if aspect_name == 'deployed':
                    value = value.lower() == 'true'
                filters[aspect_name] = value
        manager.list_robots(filters, detailed=args.detailed, sort_by=args.sort)
    elif args.command == 'edit':
        edit_args = {
            'model': args.model,
            'status': args.status,
            'hostname': args.hostname,
            'deployed': args.deployed
        }
        # Add dynamic aspects to edit_args
        if args.aspect:
            for aspect_name, aspect_value in args.aspect:
                edit_args[aspect_name] = aspect_value
                
        # Remove None values from edit_args
        edit_args = {k: v for k, v in edit_args.items() if v is not None}
        manager.edit_robot(args.name, **edit_args)
    elif args.command == 'add-aspect':
        manager.add_aspect(args.name, args.default)
    elif args.command == 'remove-aspect':
        if not args.force:
            response = input(f"Are you sure you want to remove the aspect '{args.name}'? "
                           "This cannot be undone (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled")
                return
        manager.remove_aspect(args.name)
    elif args.command == 'connect':
        if args.name not in manager.robots:
            print(f"Error: Robot '{args.name}' not found")
            sys.exit(1)
        robot = manager.robots[args.name]
        print(f"Connecting to {args.name} via hostname:{robot.hostname}...")
        connector.connect(robot.hostname, args.remote_command)
    elif args.command == 'push':
        if args.name not in manager.robots:
            print(f"Error: Robot '{args.name}' not found")
            sys.exit(1)
        robot = manager.robots[args.name]
        connector.transfer(robot.hostname, args.source_dir, args.dest_dir, pull=False)
    elif args.command == 'pull':
        if args.name not in manager.robots:
            print(f"Error: Robot '{args.name}' not found")
            sys.exit(1)
        robot = manager.robots[args.name]
        connector.transfer(robot.hostname, args.source_dir, args.dest_dir, pull=True)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main() 