import subprocess

def get_pip_info(package_name):
    try:
        output = subprocess.check_output(['pip', 'show', package_name]).decode('utf-8', 'ignore')
    except subprocess.CalledProcessError:
        output = ""
    results = {}
    if not isinstance(output, str):
        output = output.decode('utf-8', 'ignore')
    for line in output.split('\n'):
        a = line.split(": ")
        if len(a) == 2:
            results[a[0]] = a[1]
    for key in ['Name', 'Home-page', 'Version']:
        if key not in results:
            results[key] = None
    return results
