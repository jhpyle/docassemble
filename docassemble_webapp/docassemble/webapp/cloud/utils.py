from docassemble.webapp.config import (
    s3_config,
    S3_ENABLED,
    azure_config,
    AZURE_ENABLED,
    daconfig,
)
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.utils.logger import logmessage

def get_cloud():
    if S3_ENABLED:
        import docassemble.base.amazon  # pylint: disable=import-outside-toplevel
        the_cloud = docassemble.base.amazon.S3Object(s3_config)
    elif AZURE_ENABLED:
        import docassemble.base.microsoft  # pylint: disable=import-outside-toplevel
        the_cloud = docassemble.base.microsoft.AzureObject(azure_config)
    else:
        the_cloud = None
    return the_cloud


def get_custom_cloud(provider, config):
    if provider is None or config is None:
        return None
    if provider == 's3':
        import docassemble.base.amazon  # pylint: disable=import-outside-toplevel
        the_cloud = docassemble.base.amazon.S3Object(config)
    elif provider == 'azure':
        import docassemble.base.microsoft  # pylint: disable=import-outside-toplevel
        the_cloud = docassemble.base.microsoft.AzureObject(config)
    else:
        the_cloud = None
    return the_cloud

cloud = get_cloud()

cloud_cache = {}


@hookimpl
def cloud_custom(provider, config):
    config_id = str(provider) + str(config)
    if config_id in cloud_cache:
        return cloud_cache[config_id]
    the_config = daconfig.get(config, None)
    if the_config is None or not isinstance(the_config, dict):
        logmessage("cloud_custom: invalid cloud configuration")
        return None
    cloud_cache[config_id] = get_custom_cloud(provider, the_config)
    return cloud_cache[config_id]

@hookimpl(specname="get_cloud")
def return_cloud():
    return cloud
