from minio import Minio
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists
import sys
import re

hostname = re.sub(r'^https?://', r'', sys.argv[1])

minioClient = Minio(hostname,
                    access_key=sys.argv[2],
                    secret_key=sys.argv[3],
                    secure=False)

try:
    minioClient.make_bucket(sys.argv[4])
except BucketAlreadyOwnedByYou as err:
    sys.stderr.write("Bucket already exists\n")
except BucketAlreadyExists as err:
    sys.stderr.write("Bucket already exists\n")
except ResponseError as err:
    raise
