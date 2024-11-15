#!/usr/bin/env python3
import argparse
import sys
from robot_manager import RobotManager

def main():
    manager = RobotManager()
    
    parser = argparse.ArgumentParser(description='Robot Fleet Management System')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new robot')
    create_parser.add_argument('name', help='Name of the robot')
    create_parser.add_argument('model', help='Model of the robot')
    
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
    
    args = parser.parse_args()
    
    if args.command == 'create':
        manager.create_robot(args.name, args.model)
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
        manager.list_robots(filters, detailed=args.detailed)
    elif args.command == 'edit':
        edit_args = {
            'model': args.model,
            'status': args.status,
            'firmware_version': args.firmware,
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
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main() 