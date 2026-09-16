import os
import sys
import time
from datetime import datetime
from functools import wraps


def require_env(var_name: str, hint: str = None) -> str:
    value = os.getenv(var_name)
    if not value:
        message = f"Missing required environment variable: {var_name}"
        if hint:
            message += f" — {hint}"
        raise EnvironmentError(message)
    return value


def safe_call(fallback_message: str = "Sorry, something went wrong. Please try again."):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                print(f"[error] {func.__name__} failed: {error}", file=sys.stderr)
                return fallback_message
        return wrapper
    return decorator


def retry_call(func, *args, retries: int = 2, delay: float = 1.0, retry_on=(Exception,), **kwargs):
    last_error = None
    for attempt in range(retries + 1):
        try:
            return func(*args, **kwargs)
        except retry_on as error:
            last_error = error
            if attempt < retries:
                time.sleep(delay)
    raise last_error


def mask_key(key: str, visible: int = 4) -> str:
    if not key:
        return "(missing)"
    if len(key) <= visible:
        return "*" * len(key)
    return "*" * (len(key) - visible) + key[-visible:]


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"


def supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def colorize(text: str, color: str, enabled: bool = True) -> str:
    if not enabled or not color:
        return text
    return f"{color}{text}{Colors.RESET}"


def print_banner(title: str, subtitle: str = "", width: int = 44) -> None:
    top = "┌" + "─" * (width - 2) + "┐"
    bottom = "└" + "─" * (width - 2) + "┘"
    print(top)
    print("│" + title.center(width - 2) + "│")
    if subtitle:
        print("│" + subtitle.center(width - 2) + "│")
    print(bottom)


def show_typing_indicator(enabled: bool = True, label: str = "AI is typing...") -> None:
    if enabled:
        sys.stdout.write(label)
        sys.stdout.flush()


def clear_line(width: int = 40) -> None:
    sys.stdout.write("\r" + " " * width + "\r")
    sys.stdout.flush()
