import http
from typing import Optional, Dict

import requests

from src.ext_services.abstract_jsql_service import AbstractJSQLService


class RestJSQLService(AbstractJSQLService):
    def __init__(self):
        self._entry_point = "http://192.168.1.4:8079/sqltojson"
        # self._entry_point = "http://172.17.0.2:8079/sqltojson"
        # self._entry_point = "http://localhost:8079/sqltojson"

    def call_jsql(self, sql: str) -> Optional[Dict]:

        # print("call_jsql func : ")
        # print(sql)

        response = requests.post(self._entry_point, json={"sql": sql}, timeout=3)
        # print("response ",response)



        if response.status_code != http.HTTPStatus.OK:
            # print("asdas")
            raise Exception("")
        output = response.json()
        if "timestamp" not in output.keys():
            return output
        else:
            return None
