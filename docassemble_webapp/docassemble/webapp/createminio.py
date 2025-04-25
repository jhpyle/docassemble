import sys
import re
from minio import Minio

hostname = re.sub(r'^https?://', r'', sys.argv[1])

minioClient = Minio(hostname,
                    access_key=sys.argv[2],
                    secret_key=sys.argv[3],
                    secure=False)

try:
    minioClient.make_bucket(sys.argv[4])
except BaseException as err:
    sys.stderr.write("Error: " + err.__class__.__name__ + "\n")
