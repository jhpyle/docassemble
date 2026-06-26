import copy
import os
import subprocess
import sys
import tempfile

if __name__ == "__main__":
    cron_type = 'cron_daily'
    arguments = copy.deepcopy(sys.argv)
    while len(arguments) > 0:
        if arguments[0] == '-type' and len(arguments) > 1:
            arguments.pop(0)
            cron_type = arguments.pop(0)
            break
        arguments.pop(0)
    args = ['flask', '--app', 'docassemble.webapp.server', 'cron', 'run', cron_type]
    the_env = os.environ.copy()
    the_env['IN_CRON'] = 'true'
    sys.exit(subprocess.run(args, cwd=tempfile.gettempdir(), check=False, env=the_env).returncode)
