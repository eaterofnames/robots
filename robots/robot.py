"""
Robot class

Handles individual robot configuration and aspects
"""

class Robot:
    def __init__(self, name, model, hostname, status="idle", deployed=False, **aspects):
        # Core attributes are ones the user cannot change
        self.name = name
        self.model = model
        self.hostname = hostname
        self.status = status
        self.deployed = deployed
        self._core_attributes = {'name', 'model', 'hostname', 'status', 'deployed'}
        # Store dynamic aspects
        self.aspects = aspects if aspects else {}
        
    def add_aspect(self, aspect_name, default_value=None):
        """Add a new aspect to the robot"""
        if aspect_name in self._core_attributes:
            return False, f"Cannot add '{aspect_name}': it's a core attribute"
        if aspect_name in self.aspects:
            return False, f"Aspect '{aspect_name}' already exists"
        
        self.aspects[aspect_name] = default_value
        return True, f"Added aspect '{aspect_name}'"
    
    def set_aspect(self, aspect_name, value):
        """Set the value of an aspect"""
        if aspect_name in self._core_attributes:
            setattr(self, aspect_name, value)
        else:
            self.aspects[aspect_name] = value
    
    def get_aspect(self, aspect_name):
        """Get the value of an aspect"""
        if aspect_name in self._core_attributes:
            return getattr(self, aspect_name)
        return self.aspects.get(aspect_name)
        
    def to_dict(self):
        """Convert robot instance to dictionary"""
        data = {
            "name": self.name,
            "model": self.model,
            "hostname": self.hostname,
            "status": self.status,
            "deployed": self.deployed
        }
        # Add dynamic aspects
        data.update(self.aspects)
        return data
    
    def remove_aspect(self, aspect_name):
        """Remove an aspect from the robot"""
        if aspect_name in self._core_attributes:
            return False, f"Cannot remove '{aspect_name}': it's a core attribute"
        if aspect_name not in self.aspects:
            return False, f"Aspect '{aspect_name}' does not exist"
        
        del self.aspects[aspect_name]
        return True, f"Removed aspect '{aspect_name}'"
