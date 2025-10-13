from datetime import datetime, timedelta
from typing import Union
import requests

from .base import SireSunatBase

class ApiSireSunat(SireSunatBase):

    def __init__(self,ruc,user,password,version='v1'):
        super().__init__(ruc=ruc, user=user, password=password, api_version=version)

    def get_proposal_ticket(self,period:str) -> Union[str,bool]:
        self.get_access_token()
        url_base = f"{self.BASE_URI}/{self.api_version}/{self.CONTRIBUTOR_PROPOSAL_ENDPOINT}/"
        endpoint="%s%s%s"%(url_base,period,"/exportapropuesta?codTipoArchivo=0")

        try:
            response = requests.get(endpoint, headers=self._headers())
            if response.status_code == 200:
                response_data = response.json()
                return response_data["numTicket"]

            else:
                return False
        except:
            return False


    def get_file_data(self,initial_period:str,final_period:str,num_ticket:str):
        self.get_access_token()
        url_base = f"{self.BASE_URI}/{self.api_version}/{self.MASSIVE_RVIERCE_ENDPOINT}"
        endpoint = "%s/consultaestadotickets?perIni=%s&perFin=%s&page=1&perPage=200000&numTicket=%s"%(
            url_base,initial_period,final_period,num_ticket)
        try:
            response = requests.get(endpoint, headers=self._headers())
            if response.status_code == 200:
                response_data = response.json()
                data = response_data.get('registros',[{}])[0].get('archivoReporte',[''])[0]
                cod = data['codTipoAchivoReporte']
                report_name = data['nomArchivoReporte']
                content_name = data['nomArchivoContenido']
                return [cod,report_name,content_name]

            else:
                return False
        except:
            return False


    def download_zip_file_txt(self,report_name:str,report_type:str|None) -> Union[bytes,bool]:
        self.get_access_token()
        url_base = f"{self.BASE_URI}/{self.api_version}/{self.MASSIVE_RVIERCE_ENDPOINT}"
        endpoint = "%s/archivoreporte?nomArchivoReporte=%s&codTipoArchivoReporte=%s&codLibro=140000"%(
            url_base,report_name,report_type or "null")

        try:
            response = requests.get(endpoint, headers=self._headers())
            if response.status_code == 200:
              data = response.content
              return data

            else:
                return False
        except:
            return False
