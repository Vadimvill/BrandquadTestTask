import json
import time
from typing import Iterable, Any

import scrapy


class AlkotekaSpider(scrapy.Spider):
    name = "alkoteka_spider"
    allowed_domains = ["alkoteka.com"]
    city_uuid = "4a70f9e0-46ae-11e7-83ff-00155d026416"
    base_api_url = "https://alkoteka.com/web-api/v1/product"
    categories = ["https://alkoteka.com/catalog/krepkiy-alkogol", "https://alkoteka.com/catalog/vino",
                  "https://alkoteka.com/catalog/skidki"]

    def start_requests(self) -> Iterable[Any]:
        for url in self.categories:
            root_category_slug = url.split("/")[-1]
            request_url = f"{self.base_api_url}?root_category_slug={root_category_slug}&city_uuid={self.city_uuid}&per_page=51"
            yield scrapy.Request(
                f"{request_url}&page=1",
                callback=self.parse_category, meta={'page': 1, 'request_url': request_url})

    def parse_category(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to decode JSON from {response.url}")
            return
        products = data.get("results", [])

        if products:
            for product in products:
                product_url = f"{self.base_api_url}/{product.get('slug')}?city_uuid={self.city_uuid}"
                yield scrapy.Request(
                    product_url,
                    callback=self.parse_product, meta={'slug': product.get('slug')})

        next_page = response.meta['page'] + 1
        yield scrapy.Request(
            f"{response.meta['request_url']}&page={next_page}",
            callback=self.parse_category, meta={'page': next_page, 'request_url': response.meta['request_url']})

    def parse_product(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to decode JSON from {response.url}")
            return

        product = data.get('results')
        product_base_url = "https://alkoteka.com/product/"

        description_blocks = product.get('description_blocks', [])
        brand_block = next((block for block in description_blocks if block.get('title') == 'Бренд'), None)

        brand_name = None
        if brand_block and 'values' in brand_block and brand_block['values']:
            brand_name = brand_block['values'][0].get('name')

        current_price = product.get('price')
        prev_price = product.get('prev_price')
        if prev_price:
            sale_percent = ((current_price / prev_price) - 1) * (-100)
            sale_str = f"Скидка {sale_percent}%"
        else:
            prev_price = current_price
            sale_str = None

        props = {}
        for item in product.get('description_blocks', []):
            values = [value.get('name') for value in item.get('values', [])]
            result = ""
            if len(values) > 1:
                result = ", ".join(values)
            elif len(values) == 0:
                result = item.get('max')
            else:
                result = values[0]
            props[item.get('title')] = result

        props['Артикул'] = product.get('vendor_code')

        description_block = product.get('text_blocks', [])
        description = None
        if description_block:
            description = description_block[0].get('content')

        if product:
            yield {
                "timestamp": int(time.time()),
                "RPC": product.get('uuid'),
                "url": f"{product_base_url}{product.get('category').get('slug')}/{response.meta.get('slug')}",
                "title": f"{product.get('name')}, {props.get('Объем')}",
                "marketing_tags": [tag['title'] for tag in product.get('filter_labels', [])],
                "brand": brand_name,
                "section": [product.get('category').get('parent').get('name')],
                "price_data": {
                    "current": float(current_price),
                    "original": float(prev_price),
                    "sale_tag": sale_str
                },
                "stock": {
                    "in_stock": product.get('available'),
                    "count": 0
                },
                "assets": {
                    "main_image": product.get('image_url'),
                    "set_images": [product.get('image_url')],
                    "view360": [],
                    "video": []
                },
                "metadata": {
                    "__description": description,
                    **props
                },
                "variants": 0
            }
