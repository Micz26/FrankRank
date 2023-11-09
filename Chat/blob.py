from azure.storage.blob import BlobServiceClient
import time
import os 

def uploadChartToBlobStorage(fig, user):
    connect_str = "DefaultEndpointsProtocol=https;AccountName=otomotodata;AccountKey=FQ+vB6P/bdgHh2m2hmYLPqWDywq16SjAjhVfIwGrelZYrhT/ugs2ozrMotb0M6vAl94N/fG67MUZ+AStEMHcsg==;EndpointSuffix=core.windows.net"
    container_name = "charts"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blobName = f"chart_{user}{round(time.time())}.png"
    fig.figure.savefig(blobName)
    
    blob_client = blob_service_client.get_blob_client(container=container_name, blob = blobName)
    with open(file=blobName, mode="rb") as data:
        blob_client.upload_blob(data)

    os.remove(blobName)
    
    return blob_client.url