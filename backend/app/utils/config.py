import os

def get_config(name: str, fallback=None):
    return os.environ.get(name) or fallback
