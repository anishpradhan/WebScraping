import scrapy


class UsedCars(scrapy.Spider):
    name = "newcars"

    def start_requests(self):
        url = "https://www.carsguide.com.au/buy-a-car/all-new/all-states/all-locations/all-bodytypes/all-makes?sortBy=make,model&orderBy=asc&searchOffset=0&searchLimit=12"
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        cars_list_urls = response.css("div.listing-cars a.carListing.carListing-slideBtn::attr(href)").getall()
        url = 'https://www.carsguide.com.au'
        cars_urls = [url + i for i in cars_list_urls]

        for i, car in enumerate(cars_urls):
            yield scrapy.Request(car, callback=self.parse_cars, meta={'car_url': cars_urls[i]})

        next_page = response.css('li.listing-pagination-next  a::attr(href)').get()

        if next_page != 'javascript:void(0)':
            next_page_url = url + next_page
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_cars(self, response):
        car_name = response.css('h1.details-page-heading span::text').get()
        if '.' in car_name:
            car_name = car_name.replace('.', '-')

        detail_body = response.css('table.details-page-tab-table.more-details.clearfix tr')
        details = dict()
        for i in detail_body:
            title = i.css('th::text').get()
            if ' ' in title:
                title = title.replace(' ', '_')
            body = i.css('td::text, td strong::text').getall()
            body = ' '.join([i.strip() for i in body if i.strip() != ''])
            if body != '':
                details[title] = body
        seller_comments = response.css("div.details-page-tab-comments.collapse::text").get()
        seller_location = ', '.join(response.css('div.details-page-sellers-loc span::text').getall())

        features = response.css("table.details-page-tab-table.features.clearfix td::text").getall()
        tech_spec = response.xpath('//div[@class="tab-tech-specs"]//dt/text()').extract()
        tech_spec = [i.replace(' ', "_") if ' ' in i else i for i in tech_spec]
        tech_value = response.xpath(
            '//div[@class="tab-tech-specs"]//dd[(contains(@class, "icons"))]//span/@class | //dd/text()').extract()
        if len(tech_spec) == len(tech_value):
            tech_specs = {tech_spec[i][:-1]: tech_value[i] for i in range(len(tech_spec))}
        else:
            tech_specs = {}
        dealer = response.css('div.trgInsertTopTitle p::text').get()
        details['seller_location'] = seller_location
        details['seller_comments'] = seller_comments
        new_cars = {
            'car_model': car_name,
            'url': response.meta['car_url'],
            'dealer': dealer,
            'details': [details],
            'features': features,
            'tech_specs': [tech_specs]
        }
        yield new_cars
