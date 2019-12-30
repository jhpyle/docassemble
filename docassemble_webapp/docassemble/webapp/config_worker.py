from docassemble.base.config import daconfig

broker_heartbeat = 30
task_serializer = 'pickle'
accept_content = ['pickle']
result_serializer = 'pickle'
timezone = daconfig.get('timezone', 'America/New_York')
enable_utc = True
if 'celery processes' in daconfig:
    worker_concurrency = daconfig['celery processes']
