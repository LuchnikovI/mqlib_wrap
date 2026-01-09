#!/usr/bin/env python3

import logging
from mqlib_installation_utils import ensure_mqlib

logging.basicConfig(level=logging.INFO)


def main():
    ensure_mqlib()

if __name__ == "__main__":
    main()
