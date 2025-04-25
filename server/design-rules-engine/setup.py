import os

def create_directories():
    """Create necessary directories."""
    directories = [
        "rules",
        "validators",
        "utils",
        "tests",
        "data"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # Create __init__.py for Python packages
        if directory != "data":
            init_file = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    pass
    
    print("Directories created successfully")

if __name__ == "__main__":
    print("Setting up Design Rules Engine...")
    create_directories()
    print("Setup completed successfully!")