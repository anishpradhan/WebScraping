import scrapy, requests
import random


class Dealers(scrapy.Spider):
    name = "dealers"
    # def start_requests(self):
    # url = 'https://www.carsguide.com.au/car-dealers/'
    url_list = ['https://www.carsguide.com.au/car-dealers/page' + str(i) for i in range(301,336)]
    start_urls = url_list

    def parse(self, response, **kwargs):
        dealers_row = response.css('div.dealer-listings.row div.dealerListing')
        for dealers in dealers_row:
            name_div = dealers.css('div.dealerListing--mainInfo')
            name = name_div.css('div.dealerListing--name a::text').get()
            url_link = name_div.css('div.dealerListing--name a::attr(href)').get()
            url = "https://www.carsguide.com.au" + url_link

            dealer_details = {
                'name': name,
                'url': url,
            }
            request = scrapy.Request(url, callback=self.parse_dealer,
                                     meta={'dealer_details': dealer_details})
            yield request

    def parse_dealer(self, response):
        contactDetail = response.css('ul.dealerDetails--contactDetailsDesktop.list-unstyled')
        phone = contactDetail.css('li span::text').get()
        car_id = contactDetail.css('li::text').getall()
        car_id = [i.strip() for i in car_id if i.strip() != ''][0]
        address = contactDetail.css('li a::text').get()
        dealer_website = response.css(
            'div.dealerDetails--infoSection1 ul.list-unstyled li a[data-gtm-label="dealer website"]::attr(href)').get()
        dealer_facebook = response.css(
            'div.dealerDetails--infoSection1 ul.list-unstyled li a[data-gtm-label="dealer social facebook"]::attr(href)').get()
        dealer_youtube = response.css(
            'div.dealerDetails--infoSection1 ul.list-unstyled li a[data-gtm-label="dealer social youtube"]::attr(href)').get()
        days = response.css('div.dealerDetails--infoSection2 label.short::text').getall()
        time = response.css('div.dealerDetails--infoSection2 span::text').getall()
        opening_days = {days[i]: time[i] for i in range(len(days))}

        extra_details = response.css('div.dealerDetails--smallPrint div::text').getall()
        extra = {i.split(':')[0]: i.split(':')[1][1:] for i in extra_details}
        dealer_details = response.meta['dealer_details']
        dealer_details['detail'] = dict()
        dealer_details['detail']['phone'] = phone
        dealer_details['detail']['car_id'] = car_id
        dealer_details['detail']['address'] = address
        dealer_details['detail']['dealer_website'] = dealer_website
        dealer_details['detail']['dealer_facebook'] = dealer_facebook
        dealer_details['detail']['dealer_youtube'] = dealer_youtube
        dealer_details['detail']['opening_days'] = opening_days
        dealer_details['detail']['extra_details'] = extra
        dealer_details['cars_for_sale'] = dict()

        page_url_suffix = '&searchOffset=0&searchLimit=12'
        url = dealer_details['url'] + page_url_suffix
        requesting = scrapy.Request(url, callback=self.parse_car_for_sale,
                                    meta={'dealer_details': dealer_details}, dont_filter=True)
        yield requesting

    def parse_car_for_sale(self, response):
        car_sale_div = response.css('div.resultsGrid.resultsGrid-dealer a')
        dealer_details = response.meta['dealer_details']
        link_x = 0
        links = car_sale_div.css('a::attr(href)').getall()
        final_links = ['https://www.carsguide.com.au' + i for i in links]
        if len(final_links) >= 1:
            car_url = final_links[link_x]

            next_page_url = response.css('li.listing-pagination-next a::attr(href)').get()
            next_page_url_final = None
            if next_page_url != 'javascript:void(0)':
                if next_page_url is not None:
                    next_page_url_final = 'https://www.carsguide.com.au' + str(next_page_url)
            request_car = scrapy.Request(car_url, callback=self.parse_cars,
                                         meta={'dealer_details': dealer_details, 'final_links': final_links,
                                               'next_page_url_finale': next_page_url_final, 'link_x': link_x},
                                         dont_filter=True)
            yield request_car
        else:
            yield dealer_details

    def parse_cars(self, response):
        car_name = response.css('h1.details-page-heading span::text').get()
        if '.' in car_name:
            car_name = car_name.replace('.', '-')
        detail_body = response.css('table.details-page-tab-table.more-details.clearfix tr')
        details = dict()
        for i in detail_body:
            title = i.css('th::text').get()
            body = i.css('td::text, td strong::text').getall()
            body = ' '.join([i.strip() for i in body if i.strip() != ''])
            if body != '':
                details[title] = body

        seller_location = ', '.join(response.css('div.details-page-sellers-loc span::text').getall())

        dealer_details = response.meta['dealer_details']
        link_x = response.meta['link_x']
        final_links = response.meta['final_links']
        if car_name in dealer_details['cars_for_sale'].keys():
            random_number = random.randint(0, 500)
            car_name = car_name + '__' + str(random_number)
        dealer_details['cars_for_sale'][car_name] = dict()
        dealer_details['cars_for_sale'][car_name]['url'] = final_links[link_x]
        dealer_details['cars_for_sale'][car_name]['details'] = details
        dealer_details['cars_for_sale'][car_name]['details']['seller_location'] = seller_location

        next_page_url_finals = response.meta['next_page_url_finale']
        if len(final_links) == link_x + 1:
            if next_page_url_finals:
                yield scrapy.Request(next_page_url_finals, callback=self.parse_car_for_sale,
                                     meta={'dealer_details': dealer_details}, dont_filter=True)

            else:
                yield dealer_details
        else:
            link_x += 1
            new_url = final_links[link_x]
            request_new = scrapy.Request(new_url, callback=self.parse_cars,
                                         meta={'dealer_details': dealer_details, 'final_links': final_links,
                                               'link_x': link_x, 'next_page_url_finale': next_page_url_finals},
                                         dont_filter=True)
            yield request_new
