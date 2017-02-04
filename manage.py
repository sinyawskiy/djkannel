#!/usr/bin/env python
import os
import sys

# sys.path.append('/opt/pycharm-2.7.3/pycharm-debug.egg')
# import pydevd
# pydevd.settrace('localhost', port=21000, stdoutToServer=True, stderrToServer=True)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
