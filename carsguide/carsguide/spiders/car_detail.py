from carsguide.items import *
import requests
import scrapy


class CarDetail(scrapy.Spider):
    name = "cardetail"

    # allowed_domains = ['carsguide.com.au']

    def start_requests(self):
        url = "https://www.carsguide.com.au/price"
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        company = getattr(self, 'company', None)
        if company is not None:
            company_name = response.css('ul.cg-makes-list-all li a[data-make-name=' + company + ']::text').get()
            url = 'https://www.carsguide.com.au/' + company_name + '/all-models/price'
            request = scrapy.Request(url, callback=self.parse_cars)
            yield request
        else:
            company_name = response.css('ul.cg-makes-list-all li a::text').getall()
            for company in company_name:
                if ' ' in company:
                    company = company.replace(' ', '-')
                if '.' in company:
                    company = company.replace('.', '-')
                url = 'https://www.carsguide.com.au/' + company + '/all-models/price'

                request = scrapy.Request(url, callback=self.parse_cars, meta=dict(bacK_url=url))
                yield request

    def parse_cars(self, response, **kwargs):
        # TITLE
        title = response.css('h1.summaryContainer--heading::text, h1.summaryContainer--heading::text').get().strip()

        # DESCRIPTION
        desc_class = response.css('div.container.price-spec')
        description = desc_class.css('p::text, p *::text').getall()
        final_description = ''.join(description)

        car = {
            'name': title,
            'desc': final_description,
            'models': list()
        }
        # ALL MODELS
        all_models = response.css('table.cgNativeTable')
        if len(all_models) > 1:
            all_model_num = 1
        else:
            all_model_num = 0
        model_table = all_models[all_model_num].css('tr.cgNativeTable--row')
        links = model_table.css('td a::attr(href)').getall()
        final_links = ['https://www.carsguide.com.au' + i for i in links]
        link_x = 0
        model_names = model_table.css('td::text').getall()
        all_model_name = [i.strip() for i in model_names]
        all_model_name = [i for i in all_model_name if i != '']
        model_url = final_links[link_x]
        requesting = scrapy.Request(model_url, callback=self.parse_model_cars,
                                    meta=dict(car=car, all_model_name=all_model_name,
                                              final_links=final_links, link_x=link_x))
        yield requesting

    def parse_model_cars(self, response, **kwargs):
        desc = response.css('div.description div.summary-item.folded-item')
        about = ''.join(desc.css('p::text, p *::text').getall())

        def get_rating():
            rate = response.css('div.number-rating div::text').getall()
            final_rating = ''.join(rate)
            return final_rating

        car = response.meta['car']
        link_x = response.meta['link_x']
        final_links = response.meta['final_links']
        all_model_name = response.meta['all_model_name']
        model_name = all_model_name[link_x]
        price = response.css('div.price::text').get().strip()
        model_url = final_links[link_x]

        price_table = response.css('table#pricingSpecsTable')
        heading = price_table.css('thead tr th::text').getall()
        table_body = price_table.css('tbody tr')
        year_price = list()
        for row in table_body:
            row_detail = row.css('tr td::text, td *::text').getall()
            year = {
                'year': row_detail[0],
                heading[1]: row_detail[1],
                heading[2]: row_detail[2],
            }
            year_price.append(year)
        detail = {
            'model_name': model_name,
            'url': model_url,
            'price': price,
            'about': about,
            'rating': get_rating(),
            'year_price': year_price
        }
        car['models'].append(detail)
        if len(final_links) == link_x + 1:
            yield car
        else:
            link_x += 1
            model_url = final_links[link_x]
            request = scrapy.Request(model_url, callback=self.parse_model_cars,
                                     meta=dict(car=car, all_model_name=all_model_name,
                                               final_links=final_links, link_x=link_x))

            yield request
