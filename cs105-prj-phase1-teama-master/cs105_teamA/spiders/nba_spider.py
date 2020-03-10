import scrapy
import time
import pandas as pd
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tabulate import tabulate
from scrapy.linkextractors import LinkExtractor
from selenium import webdriver
import selenium
from bs4 import BeautifulSoup
import re


class nbastatsSpider(scrapy.Spider):
    name = "nba_stats"
    start_urls = ['https://stats.nba.com/players/list/']

    # open the list of players
    def parse(self, response):
        # use web driver to open the website forcing a render of the js elements

        driver = webdriver.Chrome('/chromedriver.exe')
        driver.get(self.start_urls[0])
        WebDriverWait(driver, 300).until(EC.presence_of_all_elements_located)

        main_window = driver.current_window_handle

        # use beautifulsoup to help the render and copy the html from the rendered page
        nba_soup = BeautifulSoup(driver.page_source, 'lxml')

        pass_first = 1 

        links = nba_soup.find_all('a', href=True)
        # use beautifulsoup to select the links and follow them!
        for link in links:
            if not link['href'].find("/player/"):  # if it's a player link we follow it
                # for some reason,the first page is never right
                # also, used to skip pass_first # of pages to prevent re- scrubbing
                if pass_first:
                    pass_first -= 1
                    continue

                driver.execute_script("window.open('');")  # open new tab
                driver.switch_to.window(driver.window_handles[1])  # switch to new tab

                # get/create the player stats page url
                tmp_href = link['href']  # get the href
                tmp_link = tmp_href+'traditional/'  # add the location of the desired table
                tmp_link_full = response.urljoin(tmp_link)  # create the url

                driver.get(tmp_link_full)  # navigate to new site
                WebDriverWait(driver, 9999).until(EC.presence_of_all_elements_located)  # wait for the page to load
                time.sleep(10)  # wait a second to avoid ddosing the nba (again)

                # get the data
                player_soup = BeautifulSoup(driver.page_source, 'lxml')

                player_fname = player_soup.find("p", class_="player-summary__first-name").get_text()
                player_lname = player_soup.find("p", class_="player-summary__last-name").get_text()

                row = ''
                player_table = player_soup.find_all('table')[0].find_all('td')
                for columns in player_table:
                    row += ',' + columns.get_text()

                player_line_output = (player_lname + ',' + player_fname + row).replace(" ", "").replace("\n", "")
                # scrub whitespace and newlines
                player_line_output = (player_line_output + '\n')

                with open('output.txt', 'a') as output_file:
                    output_file.write(player_line_output)

                driver.close()  # close this tab
                driver.switch_to.window(main_window)  # go back to the player list page
        output_file.close()
        driver.quit()  # close the driver

    def access_player_page(self, response):
        driver = webdriver.Chrome('/chromedriver.exe')
        driver.implicitly_wait(1)
        driver.get(response.url)
        # change to EC.presence_of_element_located(%whatever table we need%)?
        WebDriverWait(driver, 90).until(EC.presence_of_all_elements_located)


        # close the driver
        driver.quit()