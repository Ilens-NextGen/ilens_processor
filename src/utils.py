import os
from typing import Any, Callable, TypeVar, Optional as Opt, Union

T = TypeVar('T', bound=Any)
MISSING = object()

def getenv(name, default: str=MISSING) -> str: # type: ignore[assignment]
    """Get environment variable or return default value."""
    try:
        return os.environ[name]
    except KeyError:
        if default is MISSING:
            raise RuntimeError(
                f"Environment variable {name!r} is not set."
            ) from None
        return default
        

def getlistenv(name, default: list=MISSING) -> list[str]: # type: ignore[assignment]
    """Get environment variable or return default value."""
    try:
        return os.environ[name].split(',')
    except KeyError:
        if default is MISSING:
            raise RuntimeError(
                f"Environment variable {name!r} is not set."
            ) from None
        return default
    
def getintenv(name, default: int=MISSING) -> int: # type: ignore[assignment]
    """Get environment variable or return default value."""
    try:
        return int(os.environ[name])
    except KeyError:
        if default is MISSING:
            raise RuntimeError(
                f"Environment variable {name!r} is not set."
            ) from None
        return default
    
def getfloatenv(name, default: float=MISSING) -> float: # type: ignore[assignment]
    """Get environment variable or return default value."""
    try:
        return float(os.environ[name])
    except KeyError:
        if default is MISSING:
            raise RuntimeError(
                f"Environment variable {name!r} is not set."
            ) from None
        return default
    
def getenvbool(name, default: bool=MISSING) -> bool: # type: ignore[assignment]
    """Get environment variable or return default value."""
    try:
        return os.environ[name].lower() in ['true', '1', 'yes']
    except KeyError:
        if default is MISSING:
            raise RuntimeError(
                f"Environment variable {name!r} is not set."
            ) from None
        return default
