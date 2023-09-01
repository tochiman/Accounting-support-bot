import yaml
import requests
from requests.auth import HTTPBasicAuth
    
class OperatorAPI():
    def __init__(self) -> None:
        # Open file of YAML-Config...
        with open('./config.yaml','r') as yml:
            yml_conf=yaml.safe_load(yml)
            self.name=yml_conf['nextcloud']['name']
            self.AppPass=yml_conf['nextcloud']['AppPass']

        self.BaseURI="https://nextcloud.tochiman.com/"
        self.UploadFolder = "nextcloud-data/"

    def make_folder(self, folder_name: str) -> int:
        URI = self.BaseURI + f"remote.php/dav/files/{self.name}/" + self.UploadFolder + folder_name
        res = requests.request(method="MKCOL", url=URI, auth=HTTPBasicAuth(self.name, self.AppPass))
        status = res.status_code
        return status