from urllib.parse import urlparse
import requests
from configuration import keyvault


class AuthService:
    def __init__(self, url, data_partition):
        self.url = url
        self.host = urlparse(url=url).hostname
        self.data_partition = data_partition

    def get_endpoint_id(self, subject_token):
        url = f"https://api.delfi.slb.com/ccm/dataPartitionList/v2/dataPartitions/{self.data_partition}"

        payload = ""
        headers = {
            "accept": "application/json",
            "appkey": "slAxZPVhPSTH9Ij45Rm6noymBgj4pQpZ",
            "Authorization": f"Bearer {subject_token}"
        }

        response = requests.request("GET", url, data=payload, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            endpoint_id = response_json.get("endpointId")
            print(f"{endpoint_id=}")
            return endpoint_id

    def get_resource_id(self, endpoint_id, subject_token):
        url = f"https://api.delfi.slb.com/ccm/endpointRegistry/v1/dataDeployments/{endpoint_id}"
        payload = ""
        headers = {
            "accept": "application/json",
            "appkey": "slAxZPVhPSTH9Ij45Rm6noymBgj4pQpZ",
            "Authorization": f"Bearer {subject_token}"
        }

        response = requests.request("GET", url, data=payload, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            resource_id = response_json.get("resource").get("resourceId")
            print(f"{resource_id=}")
            return resource_id
        else:
            print(f"{response=}")

    def get_subject_token(self):
        SCOPE = f"{keyvault["evd-ltops"]["scope"]} ccm-data-partition-list-cfsservice.slbservice.com {keyvault["evd-ltops"]["client_id"]} e9be745d9a754cf380da64a316a75396"
        response = requests.request(method="POST",
                                    url=keyvault["evd-ltops"]["token_url"],
                                    headers={"content-type": "application/x-www-form-urlencoded"},
                                    data=f"grant_type=client_credentials&client_id={keyvault["evd-ltops"]["client_id"]}&client_secret={keyvault["evd-ltops"]["client_secret"]}&scope={SCOPE}")
        if response.status_code == 200:
            response_json = response.json()
            access_token = response_json.get("access_token")
            # print(f"{access_token}")
            return access_token

    def generate_token(self, resource_id, subject_token):
        payload = f"grant_type=token-exchange&subject_token={subject_token}&subject_token_type=urn:ietf:params:oauth:token-type:access_token&requested_token_type=urn:ietf:params:oauth:token-type:access_token&resource={resource_id}&client_id={keyvault["evd-ltops"]["client_id"]}&client_secret={keyvault["evd-ltops"]["client_secret"]}"
        response = requests.request(method="POST",
                                    url="https://csi.slb.com/v2alpha/token",
                                    headers={"content-type": "application/x-www-form-urlencoded"},
                                    data=payload)
        if response.status_code == 200:
            response_json = response.json()
            access_token = response_json.get("access_token")
            print(f"{access_token=}")
            return access_token


if __name__ == "__main__":
    service_url = "https://happyme.managed-osdu.cloud.slb-ds.com/api/storage/v1"
    data_partition_id = "admedev01-dp3"
    auth_service = AuthService(service_url, data_partition_id)
    token = auth_service.get_subject_token()
    endpointId = auth_service.get_endpoint_id(token)
    resourceId = auth_service.get_resource_id(endpointId, token)
    exchange_token = auth_service.generate_token(resourceId, token)
