from robot import Robot
import json
import os
from tabulate import tabulate

class RobotManager:
    def __init__(self):
        self.robots = {}
        self.data_file = 'robots.json'
        self._load_robots()
    
    def _load_robots(self):
        """Load robots from JSON file if it exists"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.robots = {name: Robot(**config) for name, config in data.items()}
    
    def _save_robots(self):
        """Save robots to JSON file"""
        data = {name: robot.to_dict() for name, robot in self.robots.items()}
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_robot(self, name, model):
        """Create a new robot"""
        if name in self.robots:
            print(f"Error: Robot '{name}' already exists")
            return
        
        self.robots[name] = Robot(name=name, model=model)
        self._save_robots()
        print(f"Robot '{name}' (model: {model}) created successfully")
    
    def inspect_robot(self, name):
        """Display robot configuration details"""
        if name not in self.robots:
            print(f"Error: Robot '{name}' not found")
            return
        
        robot = self.robots[name]
        print("Configuration:")
        print("  %-20s %-10s " % ("Aspect", "Value"))
        print("  %-20s %-10s " % ("------", "----"))
        for key, value in robot.to_dict().items():
            print("  %-20s %-10s" % (key, value))
    
    def get_robot_status(self, name):
        """Get the current status of a robot"""
        if name not in self.robots:
            print(f"Error: Robot '{name}' not found")
            return
        
        robot = self.robots[name]
        print(f"\nRobot: {name}")
        print(f"Status: {robot.status}")
    
    def list_robots(self, filters=None, detailed=False):
        """List all registered robots and their status with optional filters"""
        if not self.robots:
            print("No robots registered")
            return
        
        # ANSI color codes
        GREEN = '\033[92m'
        GREY = '\033[90m'
        RESET = '\033[0m'
        
        # Filter robots based on criteria
        filtered_robots = self.robots.copy()
        if filters:
            for name, robot in self.robots.items():
                robot_dict = robot.to_dict()
                for key, value in filters.items():
                    if robot_dict.get(key) != value:
                        filtered_robots.pop(name, None)
                        break
        
        if not filtered_robots:
            print("No robots match the specified filters")
            return
            
        
        # Get all unique custom aspects across all robots
        custom_aspects = set()
        if detailed:
            for robot in filtered_robots.values():
                custom_aspects.update(robot.aspects.keys())
        
        # Create header
        headers = ["Name", "Model", "Hostname", "Status"]
        if detailed and custom_aspects:
            headers.extend(sorted(custom_aspects))
        
        # Build rows to add to the table
        listed_robots = []
        for name, robot in filtered_robots.items():
            # make deployed robots pretty
            color = GREEN if robot.deployed else GREY

            # core values first
            values = [
                f"{color}{name}{RESET}",
                f"{robot.model}",
                f"{robot.hostname}",
                f"{robot.status}",
            ]

            # if we're in detailed mode, add custom aspects
            if detailed and  custom_aspects:
                for aspect in sorted(custom_aspects):
                    values.append(str(robot.aspects.get(aspect, '-')))
            
            # add this to the table to be printed
            listed_robots.append(values)
        
        # Output printing from list_robots
        print("\nRobots:")
        print(tabulate(listed_robots, headers))

    
    def add_aspect(self, aspect_name, default_value=None):
        """Add a new aspect to all robots"""
        if not self.robots:
            print("No robots registered")
            return
            
        success_count = 0
        for robot in self.robots.values():
            success, message = robot.add_aspect(aspect_name, default_value)
            if success:
                success_count += 1
            else:
                print(f"Robot {robot.name}: {message}")
                
        if success_count > 0:
            print(f"Added aspect '{aspect_name}' to {success_count} robots")
            if default_value is not None:
                print(f"Default value set to: {default_value}")
            self._save_robots()
    
    def remove_aspect(self, aspect_name):
        """Remove an aspect from all robots"""
        if not self.robots:
            print("No robots registered")
            return
            
        success_count = 0
        for robot in self.robots.values():
            success, message = robot.remove_aspect(aspect_name)
            if success:
                success_count += 1
            else:
                print(f"Robot {robot.name}: {message}")
                
        if success_count > 0:
            print(f"Removed aspect '{aspect_name}' from {success_count} robots")
            self._save_robots()
    
    def edit_robot(self, name, **kwargs):
        """Edit robot attributes and aspects"""
        if name not in self.robots:
            print(f"Error: Robot '{name}' not found")
            return
            
        robot = self.robots[name]
        
        # Convert string boolean values to actual booleans
        if 'deployed' in kwargs:
            kwargs['deployed'] = kwargs['deployed'].lower() == 'true'
            
        # Update robot attributes and aspects
        for key, value in kwargs.items():
            robot.set_aspect(key, value)
            print(f"Updated {key} to: {value}")
        
        self._save_robots()
  