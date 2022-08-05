from docassemble.base.config import s3_config, S3_ENABLED, azure_config, AZURE_ENABLED
import docassemble.base.amazon
import docassemble.base.microsoft


def get_cloud():
    if S3_ENABLED:
        cloud = docassemble.base.amazon.s3object(s3_config)
    elif AZURE_ENABLED:
        cloud = docassemble.base.microsoft.azureobject(azure_config)
    else:
        cloud = None
    return cloud


def get_custom_cloud(provider, config):
    if provider is None or config is None:
        return None
    if provider == 's3':
        cloud = docassemble.base.amazon.s3object(config)
    elif provider == 'azure':
        cloud = docassemble.base.microsoft.azureobject(config)
    else:
        cloud = None
    return cloud
