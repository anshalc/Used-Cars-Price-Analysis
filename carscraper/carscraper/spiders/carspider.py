import scrapy
import json
import os


class CarspiderSpider(scrapy.Spider):
    name = "carspider"
    allowed_domains = ["www.autotrader.ca"]
    start_urls = ["https://www.autotrader.ca"]

    def parse(self, response):
        yield from self.get_cars(response)
        with open('Brands.json', 'r') as f:
            data = json.load(f)
        
        for item in data:
            brand = item["Brand"]
            link = item["URL"]
            yield scrapy.Request(url = link, callback = self.extract_car_links, meta = {'brand': brand})





    def get_cars(self, response):
        cars = response.css('option::text').getall()[1:-1]
        for car in cars:
            car = car.strip()
            link = car.replace(" ", "%20")
            yield{
                "Brand": car,
                "URL": "https://www.autotrader.ca/cars/" + link + "/?rcp=15&rcs=0&srt=35&prx=-1&loc=British%20Columbia&hprc=True&wcp=True&inMarket=advancedSearch"
            }
    
    def extract_car_links(self, response):
        counter = 0
        urls = response.css("a.inner-link::attr('href')").get_all()
        cars = response.css("spam.title-with-trim::text").get_all()
        for car, url in zip(cars, urls):
            result = {
                "Car-Title": car.strip(),
                "Active-URL": url
            }

            filename = response.meta['brand'] + '.json'
            if not os.path.exists(filename):
                with open(filename, 'w'):
                    json.dump([result], f)
            else:
                with open(filename, 'r+') as f:
                    data = json.load(f)
                    data.append(result)
                    f.seek(0)
                    json.dump(data, f)
        self.counter += 15
        next_link = response.url.replace("rcs="+str(self.counter - 15), "rcs="+str(self.counter))


