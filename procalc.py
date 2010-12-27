#!/usr/bin/python
# coding: utf-8

import sys
from procalc.main import ProCalcApp

if __name__ == '__main__':
    app = ProCalcApp()
    try:
        app.run()
    except KeyboardInterrupt:
        sys.exit(2)

