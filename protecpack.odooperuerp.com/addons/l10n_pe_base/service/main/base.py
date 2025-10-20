from datetime import datetime, timedelta
from typing import Union
import os

import requests
from dotenv import load_dotenv

load_dotenv()

class APIEndpoints:
    @property
    def SECURITY_URI(self):
        return f"https://api-seguridad.sunat.gob.pe/{self.api_version}/clientessol"

    BASE_URI = "https://api-sire.sunat.gob.pe"
    MASSIVE_RVIERCE_ENDPOINT = "contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/masivo"
    CONTRIBUTOR_PROPOSAL_ENDPOINT = "contribuyente/migeigv/libros/rvie/propuesta/web/propuesta"


class SireSunatBase(APIEndpoints):
    def __init__(self, api_version='v1', ruc=None, user=None, password=None):
        self._client_id = os.getenv('CLIENT_ID')
        self._client_secret = os.getenv('CLIENT_SECRET')
        self._access_token = None
        self._expiration = datetime(2000, 1, 1)
        self.api_version = api_version
        self.ruc = ruc
        self.user = user
        self.password = password

    def get_access_token(self):
        if not self._access_token or self._token_is_expired():
            access_token, expires_in = self._request_access_token()
            self._access_token = access_token
            self._expiration = datetime.now() + timedelta(seconds=int(expires_in))
        return self._access_token

    def _token_is_expired(self) -> bool:
        return datetime.now() >= self._expiration

    def _request_access_token(self):
        print("new token")
        url = f"{self.SECURITY_URI}/{self._client_id}/oauth2/token/"
        username = "%s%s"%(self.ruc,self.user)
        payload = "grant_type=password&scope=%s&client_id=%s&client_secret=%s&username=%s&password=%s"%(
                     self.BASE_URI,self._client_id,self._client_secret,username,self.password)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'BIGipServerpool-e-plataformaunica-https=!3hiPNwz/51YQHNAg5/qxSLLY3Weh952tnMKBGAvrISwbyn6Gf8p/uIbSZxcwD2oiTi91ZjR3GafHZg==; TS019e7fc2=014dc399cb23b95460f8d41b0d0f5e664931cecb225ac8102749f38e8cf38de138dbbca285ca0be245f1c4ad7d86d011929033df40'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                response_data = response.json()
                return response_data["access_token"], response_data["expires_in"]
            else:
                return None,1
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud: {e}")
            return None,1

    def _headers(self):
        return {
            'Authorization': f"Bearer {self._access_token}",
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }