import os
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env_path = os.path.join(project_root, '.env')

load_dotenv(dotenv_path=env_path)


class Settings:
    USE_PROXIES = os.getenv('USE_PROXIES').lower() == 'true'
    PROXIES_ADDR_LIST = os.getenv('PROXY_ADDR_LIST')
    PROXY_LOGIN_PASSWORD = os.getenv('PROXY_LOGIN_PASSWORD')

    @property
    def PROXIES_LIST(self):
        proxy_addr_list = self.PROXIES_ADDR_LIST.split(",")
        proxy_list = []
        for item in proxy_addr_list:
            proxy_list.append(f"https://{self.PROXY_LOGIN_PASSWORD}@{item}")
        return proxy_list


settings = Settings()
