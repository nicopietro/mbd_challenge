import structlog

__version__ = "1.0.0"

logger = structlog.get_logger().bind(logger=__name__, version=__version__)
