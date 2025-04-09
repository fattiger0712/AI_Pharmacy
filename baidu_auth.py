import requests
import time
from config import BAIDU_API_KEY, BAIDU_SECRET_KEY


class BaiduAuth:
    _token_cache = None
    _token_expire = 0

    @classmethod
    def get_access_token(cls):
        if time.time() < cls._token_expire:
            return cls._token_cache

        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": BAIDU_API_KEY,
            "client_secret": BAIDU_SECRET_KEY
        }

        response = requests.post(url, params=params)
        if response.status_code == 200:
            data = response.json()
            cls._token_cache = data["access_token"]
            cls._token_expire = time.time() + data["expires_in"] - 300  # 提前5分钟刷新
            return cls._token_cache
        else:
            raise Exception(f"鉴权失败：{response.text}")
