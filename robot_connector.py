from robot import Robot
import subprocess
import sys


class RobotConnector:   
    def connect(self, hostname, remote_command=None):
        """Establish SSH connection to robot"""
        if not hostname:
            print("Error: No hostname provided")
            return False
            
        try:
            print(f"Connecting to {hostname}...")
            if remote_command:
                print(f"Running command: {remote_command}")
                subprocess.run(['ssh', hostname, remote_command], check=True)
            else:
                subprocess.run(['ssh', hostname], check=True)
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to connect to {hostname}")
            return False
        except KeyboardInterrupt:
            print("\nConnection terminated by user")
            return False