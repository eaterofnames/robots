"""
Robot Connector

Handles remote connection tasks for robots
"""

import subprocess


class RobotConnector:
    def __init__(self, config=None):
        """Initialize RobotConnector with optional config
        
        Args:
            config: Configuration dictionary containing rsync-options
        """
        self.config = config or {}
        self.rsync_options = self.config.get('rsync-options')
        self.ssh_user = self.config.get('ssh-user', 'default_user')
        self.ssh_key_path = self.config.get('ssh-key-path', '/path/to/default/key')
            
    def connect(self, hostname, remote_command=None):
        """Establish SSH connection to robot"""
        if not hostname:
            print("Error: No hostname provided")
            return False
            
        try:
            print(f"Connecting to {hostname}...")

            # Create ssh_options from config values:
            ssh_options = ['-o', f'User={self.ssh_user}', '-o', f'IdentityFile={self.ssh_key_path}']
            
            # Run a command as well if it was provided
            if remote_command:
                print(f"Running command: {remote_command}")
                subprocess.run(['ssh'] + ssh_options + [hostname, remote_command], check=True)
            else:
                subprocess.run(['ssh'] + ssh_options + [hostname], check=True)
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to connect to {hostname}")
            return False
        except KeyboardInterrupt:
            print("\nConnection terminated by user")
            return False
            
    def transfer(self, hostname, source_path, dest_path, pull=False):
        """Transfer files between local machine and robot using rsync
        
        Args:
            hostname: Robot's hostname
            source_path: Path to source directory/file
            dest_path: Path to destination directory/file
            pull: If True, pull from robot. If False, push to robot (default: False)
        """
        if not hostname or not source_path or not dest_path:
            print("Error: Missing required arguments (hostname, source_path, or dest_path)")
            return False
            
        try:
            direction = "from" if pull else "to"
            print(f"Transferring files {direction} {hostname}...")
            
            # For pull operations, prefix the source with hostname:
            # For push operations, prefix the destination with hostname:
            if pull:
                source = f"{hostname}:{source_path}"
                dest = dest_path
            else:
                source = source_path
                dest = f"{hostname}:{dest_path}"
                
            cmd = ['rsync'] + self.rsync_options + [source, dest]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to transfer files {direction} {hostname}")
            return False
        except KeyboardInterrupt:
            print("\nFile transfer terminated by user")
            return False
    