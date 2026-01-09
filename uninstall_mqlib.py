#!/usr/bin/env python3

import logging
from mqlib_installation_utils import uninstall_mqlib

logging.basicConfig(level=logging.INFO)


def main():
    uninstall_mqlib()

if __name__ == "__main__":
    main()
