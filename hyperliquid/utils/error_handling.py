"""Error handling utilities for hyperliquid-python-sdk."""
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
        # Check if address is valid hex
        int(address[2:], 16)
        return True
    except ValueError:
        return False

def retry_on_failure(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (APIError,)
) -> Callable:
    """Decorator to retry functions on failure with exponential backoff.
    
    Args:
        max_retries (int): Maximum number of retries before giving up.
        initial_delay (float): Initial delay between retries in seconds.
        max_delay (float): Maximum delay between retries in seconds.
        backoff_factor (float): Factor to multiply delay by after each retry.
        exceptions (tuple): Tuple of exceptions to retry on.
        
    Returns:
        Callable: Decorated function that will retry on failure.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            
            for retry in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if retry == max_retries:
                        break
                    
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
            
            raise last_exception  # type: ignore
            
        return wrapper
    return decorator

def validate_numeric_param(
    value: Union[int, float, str],
    param_name: str,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None
) -> Union[int, float]:
    """Validate a numeric parameter.
    
    Args:
        value: The value to validate.
        param_name: Name of the parameter (for error messages).
        min_value: Minimum allowed value (inclusive).
        max_value: Maximum allowed value (inclusive).
        
    Returns:
        Union[int, float]: The validated numeric value.
        
    Raises:
        InvalidParameterError: If validation fails.
    """
    try:
        if isinstance(value, str):
            # Try to convert string to float/int
            if '.' in value:
                num_value = float(value)
            else:
                num_value = int(value)
        else:
            num_value = value
    except (ValueError, TypeError):
        raise InvalidParameterError(f"Invalid {param_name}: must be a valid number")
    
    if min_value is not None and num_value < min_value:
        raise InvalidParameterError(
            f"Invalid {param_name}: {num_value} is less than minimum allowed value of {min_value}"
        )
    
    if max_value is not None and num_value > max_value:
        raise InvalidParameterError(
            f"Invalid {param_name}: {num_value} is greater than maximum allowed value of {max_value}"
        )
    
    return num_value
