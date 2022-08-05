import sys
import os
import docassemble.base.amazon
import docassemble.base.microsoft


def main():
    if os.environ.get('S3ENABLE', 'false') == 'true':
        s3_config = {}
        s3_config['enable'] = True
        s3_config['access key id'] = os.environ.get('S3ACCESSKEY', None)
        s3_config['secret access key'] = os.environ.get('S3SECRETACCESSKEY', None)
        s3_config['endpoint url'] = os.environ.get('S3ENDPOINTURL', None)
        s3_config['server side encryption'] = {}
        s3_config['server side encryption']['algorithm'] = os.environ.get('S3_SSE_ALGORITHM', None)
        s3_config['server side encryption']['customer algorithm'] = os.environ.get('S3_SSE_CUSTOMER_ALGORITHM', None)
        s3_config['server side encryption']['customer key'] = os.environ.get('S3_SSE_CUSTOMER_KEY', None)
        s3_config['server side encryption']['KMS key ID'] = os.environ.get('S3_SSE_KMS_KEY_ID', None)
        cloud = docassemble.base.amazon.s3object(s3_config)
    elif os.environ.get('AZUREENABLE', 'false') == 'true':
        azure_config = {}
        azure_config['enable'] = True
        azure_config['account name'] = os.environ.get('AZUREACCOUNTNAME', None)
        azure_config['account key'] = os.environ.get('AZUREACCOUNTKEY', None)
        azure_config['container'] = os.environ.get('AZURECONTAINER', None)
        cloud = docassemble.base.microsoft.azureobject(azure_config)
    else:
        sys.exit(1)
    if len(sys.argv) > 1:
        prefix = sys.argv[1]
    else:
        prefix = None
    recursive_list(cloud, prefix)


def recursive_list(cloud, prefix):
    for key in cloud.list_keys(prefix):
        if key.name != prefix and key.name.endswith('/'):
            recursive_list(cloud, key.name)
        else:
            print(key.name)

if __name__ == "__main__":
    main()
    sys.exit(0)
