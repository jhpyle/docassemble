from docassemble.base.config import s3_config, S3_ENABLED, azure_config, AZURE_ENABLED

def get_cloud():
    if S3_ENABLED:
        import docassemble.webapp.amazon
        cloud = docassemble.webapp.amazon.s3object(s3_config)
    elif AZURE_ENABLED:
        import docassemble.webapp.microsoft
        cloud = docassemble.webapp.microsoft.azureobject(azure_config)
    else:
        cloud = None
    return cloud

def get_custom_cloud(provider, config):
    if provider is None or config is None:
        return None
    if provider == 's3':
        import docassemble.webapp.amazon
        cloud = docassemble.webapp.amazon.s3object(config)
    elif provider == 'azure':
        import docassemble.webapp.microsoft
        cloud = docassemble.webapp.microsoft.azureobject(config)
    else:
        cloud = None
    return cloud
