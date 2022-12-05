"""An AWS Lambda handler decorator setting the logs as JSON."""
from functools import wraps
import logging
import os
from typing import Any, Callable, Union, Optional

# From requirements.txt
from logmatic import JsonFormatter


DEFAULT_LOG_LEVEL = logging.INFO
LOG_LEVEL = os.environ.get('LOG_LEVEL', DEFAULT_LOG_LEVEL)


def setup_logging(level: Union[str, int] = LOG_LEVEL,
                  boto_level: Optional[Union[str, int]] = None) \
        -> Callable[[Callable], Any]:
    """
    Configure a lambda_handler decorator setting the log level accordingly.

    :param level:      the desired log level.
    :param boto_level: if any, the desired boto lib logger level.

    :return: a function decorator.
    """
    def decorator(lambda_handler: Callable) -> Any:
        """
        Wrap up a decorated function.

        :params lambda_handler: the decorated function.

        :return: the decorated function result.
        """
        @wraps(lambda_handler)
        def wrapper(*handler_args, **handler_kwargs) -> Any:
            """
            Set up the logger format to json and call the decorated function.

            :param handler_args: the decorated function positional arguments.
            :param handler_kwargs: the decorated function key-value arguments.

            :return: the decorated function result.
            """
            for handler in logging.root.handlers:
                handler.setFormatter(JsonFormatter())

            try:
                logging.root.setLevel(level)
                logging.root.debug('Set root log level to: %s (default was: %s).', str(level), DEFAULT_LOG_LEVEL)

            except ValueError:
                logging.root.error('Invalid log level: %s, defaulting to %s...', str(level), DEFAULT_LOG_LEVEL)
                logging.root.setLevel(DEFAULT_LOG_LEVEL)

            if boto_level:
                logging.root.debug('Setting up boto3 log level to: %s (default: %s).', str(level), DEFAULT_LOG_LEVEL)

                try:
                    logging.getLogger('boto').setLevel(boto_level)
                    logging.getLogger('boto3').setLevel(boto_level)
                    logging.getLogger('botocore').setLevel(boto_level)

                except ValueError:
                    logging.root.error('Invalid boto3 log level: %s, defaulting to %s...', str(level),
                                       DEFAULT_LOG_LEVEL)
                    logging.getLogger('boto').setLevel(DEFAULT_LOG_LEVEL)
                    logging.getLogger('boto3').setLevel(DEFAULT_LOG_LEVEL)
                    logging.getLogger('botocore').setLevel(DEFAULT_LOG_LEVEL)

            # Execute lambda handler.
            return lambda_handler(*handler_args, **handler_kwargs)

        return wrapper

    return decorator
