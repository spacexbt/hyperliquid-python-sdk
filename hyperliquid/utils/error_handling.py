from typing import Any, Callable, Optional, TypeVar, Union
import time
from functools import wraps

T = TypeVar('T')

class HyperliquidError(Exception):
    """Base exception class for Hyperliquid SDK."""
    pass

class InvalidParameterError(HyperliquidError):
    """Raised when an invalid parameter is provided."""
    pass

class APIError(HyperliquidError):
    """Raised when an API call fails."""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

def validate_address(address: str) -> bool:
    """Validate an Ethereum address.
    
    Args:
        address (str): The address to validate.
        
    Returns:
        bool: True if the address is valid, False otherwise.
    """
    if not isinstance(address, str):
        return False
    if not address.startswith('0x'):
        return False
    if len(address) != 42:
        return False
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False