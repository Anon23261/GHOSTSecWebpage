import os

# Create necessary directories
dirs = [
    'ssl',
    'logs',
    'uploads',
    'instance'
]

for dir_name in dirs:
    os.makedirs(dir_name, exist_ok=True)
    print(f'Created directory: {dir_name}')
