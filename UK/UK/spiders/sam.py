import scrapy
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from requests_html import HTMLSession


class SamSpider(scrapy.Spider):
    name = "category"
    start_urls = [
        'https://www.savvysme.com.au/business'
    ]

    def selenium(self, css, response):
        option = webdriver.ChromeOptions()
        option.add_argument("--headless")
        browser = webdriver.Chrome(executable_path='C:/Users/Anish/OneDrive/Desktop/chromedriver/chromedriver.exe',
                                   chrome_options=option)
        browser.get(response.url)
        timeout = 10
        try:
            WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
        except TimeoutException:
            print('Timed out waiting for page to load')
            browser.quit()
        return browser

    def parse(self, response, **kwargs):
        item = response.css('div#business_category_list')
        item_cat = item.css('div.item-cat')
        for i in item_cat[17:]:
            category = i.css("div.category-item-box.animateclass.noselect::text").get().strip()
            cat_id = i.css("div.category-item-box.animateclass.noselect::attr(data-target)").get().strip('#')
            sub_cat_urls = i.css(f'div#{cat_id} div.well a::attr(href)').get()
            detail = {
                'category': category,
            }
            url = 'https://www.savvysme.com.au' + sub_cat_urls
            yield scrapy.Request(url, callback=self.parse_categ, meta={'detail': detail})

    def parse_categ(self, response):
        # css = "div.result-post.result-posting-div"
        # browser = self.selenium(css, response)
        option = webdriver.ChromeOptions()
        option.add_argument("--headless")
        browser = webdriver.Chrome(executable_path='C:/Users/Anish/OneDrive/Desktop/chromedriver/chromedriver.exe',
                                   chrome_options=option)
        browser.get(response.url)
        timeout = 10
        try:
            WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.result-post.result-posting-div")))
        except TimeoutException:
            print('Timed out waiting for page to load')
            browser.quit()
        companies = browser.find_elements_by_css_selector("h2.business-title a")
        # companies = response.css('h2.business-title a::attr(href)').getall()
        for urls in companies:
            url = urls.get_attribute('href')
            url = 'https://www.savvysme.com.au' + url
            detail = response.meta['detail']
            yield scrapy.Request(url, callback=self.parse_detail,
                                 meta={'detail': detail})

    def parse_detail(self, response):
        xpath = "//p[@class='address-contact']"
        browser = self.selenium(xpath, response)
        raw_address = browser.find_elements_by_xpath("//p[@class='address-contact']")

        raw_url = browser.find_elements_by_xpath(
            "//p[contains(@class,'address-contact website-contact')]/span[contains(@class,'click-track openUrl clickable')]")
        url = raw_url[0].get_attribute("data-href")
        address = ''.join([i.text for i in raw_address])
        phone = browser.find_elements_by_xpath(
            "//p[contains(@class,'address-contact phone-contact')]/a[contains(@class,'businessphoneNumber  click-track')]")
        num = phone[0].get_attribute("onclick")
        ph_num = ''.join(re.findall(r"[0-9]+", num))

        company_name = browser.find_elements_by_xpath("//h1[contains(@class,'connect-title title')]")
        comp_name = company_name[0].text

        EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
        session = HTMLSession()
        r = session.get(url)
        r.html.render()
        email_list = []
        for re_match in re.finditer(EMAIL_REGEX, r.html.raw_html.decode()):
            company_email = re_match.group()
            email_list.append(company_email)

        clean_email_set = set(email_list)
        clean_list = list(clean_email_set)
        print(clean_list, 'dsjfisdfhdhf')

        detail = response.meta['detail']
        detail['company_name'] = comp_name
        detail['location'] = address
        detail['url'] = url
        detail['phone_number'] = ph_num
        detail['email'] = clean_list
        yield detail
