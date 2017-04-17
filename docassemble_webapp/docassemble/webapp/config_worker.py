from docassemble.base.config import daconfig

task_serializer = 'pickle'
accept_content = ['pickle']
result_serializer = 'pickle'
timezone = daconfig.get('timezone', 'America/New_York')
enable_utc = True
