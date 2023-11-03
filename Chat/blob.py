from azure.storage.blob import BlobServiceClient
import time

def uploadChartToBlobStorage(HTML, user):
    """
    Connects to azure blob storage and uploades HTML chart
    
    Retrurns:
        blob_client.url - url to chart
    """
    connect_str = "DefaultEndpointsProtocol=https;AccountName=otomotodata;AccountKey=FQ+vB6P/bdgHh2m2hmYLPqWDywq16SjAjhVfIwGrelZYrhT/ugs2ozrMotb0M6vAl94N/fG67MUZ+AStEMHcsg==;EndpointSuffix=core.windows.net"
    container_name = "charts"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blobName = f"chart_{user}{round(time.time())}.html"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob = blobName)
    blob_client.upload_blob(HTML)

    return blob_client.url