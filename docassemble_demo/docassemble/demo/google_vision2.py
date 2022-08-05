import io
import docassemble.base.util
from google.cloud import vision

__all__ = ['gv_ocr']


def gv_ocr(the_file):
    api = docassemble.base.util.DAGoogleAPI()
    client = api.google_cloud_vision_client()
    image = vision.Image()
    with io.open(the_file.path(), 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    output = ''
    for text in response.text_annotations:
        output += text.description + "\n"
    if response.error.message:
        raise Exception(response.error.message)
    return output

# def async_detect_document(gcs_source_uri, gcs_destination_uri):
#     mime_type = 'application/pdf'

#     # How many pages should be grouped into each json output file.
#     batch_size = 2

#     client = api.google_cloud_vision_client()

#     feature = vision.Feature(
#         type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

#     gcs_source = vision.GcsSource(uri=gcs_source_uri)
#     input_config = vision.InputConfig(
#         gcs_source=gcs_source, mime_type=mime_type)

#     gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
#     output_config = vision.OutputConfig(
#         gcs_destination=gcs_destination, batch_size=batch_size)

#     async_request = vision.AsyncAnnotateFileRequest(
#         features=[feature], input_config=input_config,
#         output_config=output_config)

#     operation = client.async_batch_annotate_files(
#         requests=[async_request])

#     print('Waiting for the operation to finish.')
#     operation.result(timeout=420)

#     # Once the request has completed and the output has been
#     # written to GCS, we can list all the output files.
#     storage_client = storage.Client()

#     match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
#     bucket_name = match.group(1)
#     prefix = match.group(2)

#     bucket = storage_client.get_bucket(bucket_name)

#     # List objects with the given prefix, filtering out folders.
#     blob_list = [blob for blob in list(bucket.list_blobs(
#         prefix=prefix)) if not blob.name.endswith('/')]
#     print('Output files:')
#     for blob in blob_list:
#         print(blob.name)

#     # Process the first output file from GCS.
#     # Since we specified batch_size=2, the first response contains
#     # the first two pages of the input file.
#     output = blob_list[0]

#     json_string = output.download_as_string()
#     response = json.loads(json_string)

#     # The actual response for the first page of the input file.
#     first_page_response = response['responses'][0]
#     annotation = first_page_response['fullTextAnnotation']

#     # Here we print the full text from the first page.
#     # The response contains more information:
#     # annotation/pages/blocks/paragraphs/words/symbols
#     # including confidence scores and bounding boxes
#     print('Full text:\n')
#     print(annotation['text'])
