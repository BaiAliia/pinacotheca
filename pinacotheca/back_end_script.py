import os
import pyodbc as pyo
import pandas as pd
import requests
import shutil
from PIL import Image
from torchvision import transforms
import torchvision
from azure.storage.blob import BlobClient


""" Functions """
def download_file(url, guid): #Download an image and save it in root app path
    local_filename = "C:/Users/pinacotheca/Desktop/pinacotheca/images/" + guid + ".jpg"
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return local_filename
def download_file_broken(url, guid): #Download an image and save it in root app path
    local_filename = "C:/Users/pinacotheca/Desktop/pinacotheca/broken/" + guid + ".jpg"
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return local_filename
#preparing img to extract features
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224), 
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                         std=[0.229, 0.224, 0.225]),]
    ) 

def change_image_channels (image, image_path):
  #4 channels to 3 channels
  if image.mode == "RGBA":
    r, g, b, a=image.split ()
    image=image.merge ("RGB", (r, g, b))
    image.save (image_path)
  #1 channel to 3 channels
  elif image.mode!="RGB":
    image=image.convert ("RGB")
    os.remove (image_path)
    image.save (image_path)
  return image


#connecting to azure blob storage
conn_azure_blob = BlobClient.from_connection_string(
    conn_str="DefaultEndpointsProtocol=https;AccountName=pinacothecabl;AccountKey=YUn61RAMg/KBx3m+vBv3aCBefaIfSBZCUugSUUxH5Ne7wo7VVgZwsYepwMDGQJniIAwhLN9ZNmDH+AStNvW49w==;EndpointSuffix=core.windows.net", 
    container_name="db-images", 
    blob_name="pinacothecabl")

#connecting to azure sql database
conn_azure_sql = (
    r"Driver={SQL Server};Server=pinacotheca-srv.database.windows.net;"
    "Database=pinacotheca_db;"
    "UID=pinacotheca-admin;"
    "PWD=!Pina1234"
    )
cnn_sql= pyo.connect(conn_azure_sql)

#Setting model to get features of the image
model = torchvision.models.vgg16(pretrained=True)
model.classifier = model.classifier[:-1]



#assigning table to DataFrame
sql = "SELECT * FROM dbo.paintings;"
df = pd.read_sql(sql, cnn_sql)
rootpath = "C:/Users/pinacotheca/Desktop/pinacotheca/images/"

image_feat = []
for i in range(len(df)):
    img_raw = download_file(df.iloc[i, 8],df.iloc[i, 9]) #img jpg
    conn_azure_blob.upload_blob(img_raw, overwrite = True) #file uploaded to blobstorage
    img = Image.open(img_raw)
    img = change_image_channels(img, rootpath + df.iloc[i, 9] + ".jpg")
    img = preprocess(img) # preparing image to get features
    img.unsqueeze(0)
    try:
        image_feat.append(model(img).detach().numpy()) #getting features as an numpy array
    except RuntimeError:
        download_file_broken(df.iloc[i, 8],df.iloc[i, 9])

   
df['vectors']= image_feat  
df.to_sql('dbo.paintings', cnn_sql, if_exists='replace', index = False)
cnn_sql.close()
#Done