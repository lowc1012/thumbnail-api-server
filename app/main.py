#!/usr/bin/env python3

from app.internal.api.server import start_server
from app.internal.configuration.settings import get_settings


def main():
    """Main entry point for thumbnail service"""

    # Load configuration
    settings = get_settings()

    # Start the server
    start_server(settings)


if __name__ == "__main__":
    main()
