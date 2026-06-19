from datetime import datetime
import json
import logging
import sys

class JSONFormatter(logging.Formatter):

    def formatTime(self, record, datefmt=None):
        """Returns the creation time of the LogRecord formatted with milliseconds."""
        # Convert record.created timestamp into a local datetime object
        dt = datetime.fromtimestamp(record.created)
        # Format date and time down to seconds, then slice off microsecond precision to milliseconds
        return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{int(record.msecs):03d}"

    def _safe_serialize(self, obj):
        """Recursively forces non-serializable objects into strings."""
        try:
            # default=str automatically converts datetimes, sets, and custom objects to strings
            return json.dumps(obj, default=str)
        except Exception:
            # Absolute worst-case scenario fallback (e.g., recursive loops)
            return json.dumps({
                "timestamp": obj.get("timestamp"),
                "level": obj.get("level"),
                "module": obj.get("module"),
                "function_name": obj.get("function_name"),
                "line_num": obj.get("line_num"),
                "message": {"event": "logging_error",
                            "original_msg_repr": repr(obj.get("message"))}
            })

    def format(self, record):
        # Build the foundational structured log entry
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "module": record.module,
            "function_name": record.funcName,
            "line_num": record.lineno,
        }
        if isinstance(record.msg, dict):
            log_entry["message"] = record.msg
        else:
            # Fallback for standard string messages
            log_entry["message"] = record.getMessage()

        # Capture tracebacks automatically if an exception occurred
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        # Dynamically inject keys passed via the 'extra' keyword argument
        # while ignoring standard built-in LogRecord attributes
        builtins = {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        }
        for key, value in record.__dict__.items():
            if key not in builtins:
                log_entry[key] = value

        try:
            # First attempt: Try standard, fast serialization
            return json.dumps(log_entry)
        except TypeError:
            # Second attempt: Graceful recovery if an object (like a set or datetime) fails
            return self._safe_serialize(log_entry)


def configure_logging(log_level: str):
    """
    Configure logging
    """
    log_level_attr = logging.INFO
    try:
        log_level_attr = getattr(logging, log_level.upper())
    except AttributeError as e:
        log_level_attr = logging.INFO
    logging.basicConfig(
        # format='{"timestamp": "%(asctime)s.%(msecs)03d", "level": "%(levelname)s", "module": "%(module)s", "function_name": "%(funcName)s", "line_num": %(lineno)d, "message": %(message)s}',
        datefmt='%Y-%m-%dT%H:%M:%S',
        encoding='utf-8',
        level=log_level_attr,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logging.getLogger().handlers[0].setFormatter(JSONFormatter())

    return None
