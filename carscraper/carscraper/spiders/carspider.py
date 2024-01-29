import scrapy
import json
import os
from bs4 import BeautifulSoup
import requests


class CarspiderSpider(scrapy.Spider):
    name = "carspider"
    allowed_domains = ["www.autotrader.ca"]
    start_urls = ["https://www.autotrader.ca"]

    def parse(self, response):
        self.get_cars(response)

        with open('Brands.json', 'r') as f:
            data = json.load(f)
        
        for brand, info in data.items():
            brand = info["Brand"]
            link = info["URL"]
            yield scrapy.Request(url = link, callback = self.extract_car_links, meta = {'brand': brand, 'counter': 0}, dont_filter=True)

    def get_cars(self, response):
        cars = response.css('option::text').getall()[1:-1]
        car_dict = {}
        for car in cars:
            car = car.strip()
            link = car.replace(" ", "%20")
            car_dict[car] = {
                "Brand": car,
                "URL": "https://www.autotrader.ca/cars/" + link + "?rcp=100&rcs=0&srt=35&prx=-1&loc=Toronto%2C%20ON&hprc=True&wcp=True&inMarket=advancedSearch"
            }
        if os.path.exists('Brands.json'):
            os.remove('Brands.json')
        with open('Brands.json', 'w') as f:
            json.dump(car_dict, f)


    def extract_car_links(self, response):
        counter = response.meta['counter']
        num_cars = response.meta.get('num_cars')
        num_pages = response.meta.get('num_pages')
        if counter == 0:
            num_cars = response.css('span[id="titleCount"]::text').get()
            num_cars = num_cars.replace(",","")
            num_pages = (int(num_cars.strip())//100) * 100
        print(num_cars)

        urls = response.css("a.inner-link::attr('href')").getall()
        cars = response.css("span.title-with-trim::text").getall()
        for car, url in zip(cars, urls):
            result = {
                "Car-Title": car.strip(),
                "Active-URL": url
            }
            filename = response.meta['brand'] + '.json'
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    json.dump([result], f)
            else:
                with open(filename, 'r+') as f:
                    data = json.load(f)
                    data.append(result)
                    f.seek(0)
                    json.dump(data, f)
        next_link = response.url
        while(counter < num_pages):
            next_link = response.url.replace("rcs="+str(counter), "rcs="+str(counter + 100))
            counter = counter + 100
            yield response.follow(next_link, callback = self.extract_car_links, meta = {'brand': response.meta['brand'], 'counter': counter, 'num_cars': num_cars, 'num_pages': num_pages})