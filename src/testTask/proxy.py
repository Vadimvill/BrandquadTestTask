
import logging

logger = logging.getLogger(__name__)

class ProxyMiddleware:
    def __init__(self):
        self.proxy = 'https://45.145.160.29:8000'

    def process_request(self, request, spider):
        request.meta['proxy'] = self.proxy

        logger.debug(f'Using proxy: {self.proxy} for {request.url}')

        return None  # Важно: не останавливаем обработку