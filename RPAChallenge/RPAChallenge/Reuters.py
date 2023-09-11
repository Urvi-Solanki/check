import os
import re
from datetime import datetime, timedelta
from typing import Tuple

from dateutil.parser import parse as ps
from dateutil.relativedelta import relativedelta
from retry import retry
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        TimeoutException)

from excel import Excel
from filepaths import DIRECTORIES
from logger import logger



class NewsFromReuters:

    def __init__(self) -> None:

        self.browser = Selenium()
        self.http = HTTP()
        self.excel = Excel()

    def open_website(self) -> None:
        """Opens the available web browser
            and constructs url to open the website with news posts searches.
            No return value.
        """
        base_url = "https://www.reuters.com/site-search/?query={}&section={}&offset=0&date={}"
        query_l = self.phrase.lower()
        date_l = self.set_date()
        section_l = self.set_section()

        constructed_url = base_url.format(query_l, section_l, date_l)
        print(constructed_url)

        self.browser.open_available_browser(constructed_url)
        self.browser.maximize_browser_window()

    def check_news_data_present(self):
        """ Checks if there are any search results for the given url.
        Returns a message if there are no results.
        """
        message = ""
        news_available = False
        try:
            self.browser.wait_until_element_is_visible(
                "//div[@class='search-results__sectionContainer__34n_c']", 30)
        except AssertionError:
            message = f"No news found for the searched phrase: {self.phrase}"
            news_available = False

        if self.browser.is_element_visible("//div[@class='search-results__sectionContainer__34n_c']"):
            result = self.browser.get_text(f'(//h1[@id="main-content"])')
            if f'No search results match the term "{self.phrase}"' in result:
                message = f"No news found for the searched phrase: {self.phrase}"
                news_available = False
            else:
                news_available = True

        return news_available, message

    def set_section(self) -> str:
        """Sets the section value.
        Returns section value.
        """
        if self.section == '' or self.section is None:
            sec = "all"

        elif type(self.section) == str:
            try:
                sec = self.section.lower()
            except AssertionError:
                logger.info(f"Section {self.section} is not available.")
                raise AssertionError

        else:
            logger.info(f"Section is not available.")
            raise AssertionError
        return sec

    def set_date(self) -> str:
        """Sets the value of date as required by the website.
        Returns value of date.
        """
        if self.months == '' or self.months is None:
            logger.info(f"date is not available.")
            raise AssertionError

        elif type(self.months) == int:
            try:
                if self.months == 1:
                    date_1 = "past_month"
                elif 12 >= self.months > 1:
                    date_1 = "past_year"
                elif self.months > 12:
                    date_1 = "all"
            except AssertionError:
                logger.info(f"date {self.months} is not available.")
                raise AssertionError

        else:
            logger.info(f"Section is not available.")
            raise AssertionError
        return date_1

    def is_money_present(self, input_text: str) -> bool:
        """Checks if any money string is present in the headline.
        """

        pattern_of_money = r'\$\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:dollars|USD))?\b|\b\d+\s*(?:dollars|USD)\b'
        match = re.findall(pattern_of_money, input_text)
        if match:
            return True
        else:
            return False

    def count_of_search_string(self, input_string: str, search_string: str) -> int:
        """Returns the number of searched phrase in the headline.
        """

        for char in ".,;?!‘’":
            input_string = input_string.lower().replace(char, "")
        words = input_string.split()
        result = []

        for i in range(0, len(words), len(search_string.split())):
            result.append(' '.join(words[i:i+len(search_string.split())]))
        return result.count(search_string.lower())

    def get_news_data(self, index) -> tuple:
        """Gets all the required data from the webpage.
        (i.e. headline, date, image filename, count of phrase, count of money string and downloads image)
        """

        number_of_results = self.browser.get_text(
            f'(//span[@class = "text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_6__1qUJ5 count"])')
        count = 0

        image_container = self.browser.is_element_enabled(
            f'(//div[@class="media-story-card__placement-container__1R55-"])[{index}]')

        if image_container:

            video_element = self.browser.is_element_enabled(
                f'(//div[@class="media-story-card__image-container__gQPAN"])[{index}]//div[@class="media-story-card__media__27Yc8 media__symbol__1-WHq media__corner__-C897"]')

            if video_element:
                print("This item contains a video.")
                image_src = self.browser.get_element_attribute(
                    f'(//div[@class="media-story-card__image-container__gQPAN"])[{index}]//div[@class="styles__image-container__skIG1"]//img)', 'src')
            else:
                print("This item does not contain a video.")
                image_src = self.browser.get_element_attribute(
                    f'(//div[@class="media-story-card__image-container__gQPAN"])[{index}]//div[@class="styles__image-container__skIG1 styles__cover__2dX1S styles__center_center__1AaPV styles__apply-ratio__1_FYQ styles__transition__1DEuZ"]//img', 'src')

            headline = self.browser.get_text(
                f'(//h3[@class="text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_6__1qUJ5 heading__base__2T28j heading__heading_6__RtD9P"])[{index}]')

            date = self.browser.get_text(
                f'(//time[@class="text__text__1FZLe text__inherit-color__3208F text__regular__2N1Xr text__extra_small__1Mw6v body__base__22dCE body__extra_small_body__3QTYe media-story-card__time__2i9EK"])[{index}]')

            image_filename = f'image_news{index}.png'

            image_path = os.path.join(
                DIRECTORIES.IMAGE_PATH, image_filename)
            self.download_picture(url=image_src, target_file=image_path)

            money_present = self.is_money_present(headline)

            count_phrase = self.count_of_search_string(
                headline, self.phrase.lower())

        else:
            headline = self.browser.get_text(
                f'(//li[@class="search-results__item__2oqiX"])[{index}]//a[@class="text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_6__1qUJ5 heading__base__2T28j heading__heading_6__RtD9P text-story-card__title__3R37x"]')

            date = self.browser.get_text(
                f'(//li[@class="search-results__item__2oqiX"])[{index}]//time[@class="text__text__1FZLe text__inherit-color__3208F text__regular__2N1Xr text__extra_small__1Mw6v text-story-card__time__2w0XM"]')

            image_filename = ''

            money_present = self.is_money_present(headline)

            count_phrase = self.count_of_search_string(
                headline, self.phrase.lower())
        count = count + 1
        if count > 20 and count < number_of_results:
            self.next_button()

        return headline, date, image_filename, money_present, count_phrase

    def check_date_format(self, date_str: str, date_format: str) -> bool:
        """Checks the date format.
        """

        try:
            datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            return False

    def find_format(self, date_string: str) -> str:
        """Finds the correct date format for each date string.
        """
        if self.check_date_format(date_string, "%B %d, %Y"):
            date = datetime.strptime(date_string, "%B %d, %Y")

        elif self.check_date_format(date_string, "%B. %d, %Y"):
            date = datetime.strptime(date_string, "%B. %d, %Y")

        elif self.check_date_format(date_string, "%b %d, %Y"):
            date = datetime.strptime(date_string, "%b %d, %Y")

        elif self.check_date_format(date_string, "%b. %d, %Y"):
            date = datetime.strptime(date_string, "%b. %d, %Y")

        elif self.check_date_format(date_string, "%B %d %Y"):
            date = datetime.strptime(date_string, "%B %d %Y")

        elif self.check_date_format(date_string, "%b %d %Y"):
            date = datetime.strptime(date_string, "%b %d %Y")

        elif self.check_date_format(date_string, "%B. %d %Y"):
            date = datetime.strptime(date_string, "%B. %d %Y")

        elif self.check_date_format(date_string, "%b. %d %Y"):
            date = datetime.strptime(date_string, "%b. %d %Y")

        else:
            date = ps(date_string)

        return date

    def get_data_lists(self) -> tuple:
        """Gets the lists for heading, Date, Image FIle Name, Money Present, Count Phrase.
        """

        headline_list = []
        date_list = []
        image_filename_list = []
        money_present_list = []
        count_phrase_list = []

        list = self.browser.get_webelements(
            f'(//li[@class="search-results__item__2oqiX"])')
        for i in range(1, len(list)+1):

            title, date, image_filename, money_present, count_phrase = self.get_news_data(
                i)

            current_datetime = datetime.now()

            if 'an hour ago' in date or 'a min ago' in date:
                date_to_be_checked = datetime.today()
                date_formatted = date_to_be_checked.strftime(
                    start_date, "%m-%d-%Y")

            elif "min ago" in date:
                minutes_ago = int(date.split()[0])
                delta = timedelta(minutes=minutes_ago)
                date_time_ago = current_datetime - delta
                formatted_date = date_time_ago.strftime("%m-%d-%Y")

            elif "sec ago" in date:

                seconds_ago = int(date.split()[0])
                delta = timedelta(seconds=seconds_ago)
                date_time_ago = current_datetime - delta
                formatted_date = date_time_ago.strftime("%m-%d-%Y")

            elif "hours ago" in date:

                hours_ago = int(date.split()[0])
                delta = timedelta(hours=hours_ago)
                date_time_ago = current_datetime - delta
                formatted_date = date_time_ago.strftime("%m-%d-%Y")

            else:
                date_to_check = self.find_format(date)
                formatted_date = datetime.strftime(date_to_check, "%m-%d-%Y")

            today = datetime.today()
            start_date = today - relativedelta({self.months})
            start_date = datetime.strftime(start_date, "%m-%d-%Y")

            if formatted_date >= start_date:

                headline_list.append(title)
                date_list.append(date)
                image_filename_list.append(image_filename)
                money_present_list.append(money_present)
                count_phrase_list.append(count_phrase)

            elif date_to_be_checked < start_date:
                break

        return headline_list, date_list, image_filename_list, money_present_list, count_phrase_list

    def download_picture(self, image_src: str, image_path: str) -> None:
        """Downloads the picture from url.
        """
        HTTP().download(url=image_src, target_file=image_path)

    def next_button(self) -> None:
        """Checks if the next page button is enabled for the current page and clicks it.
        """
        next_button_enabled = self.browser.is_element_enabled(
            f'(//button[contains(@aria-label, "Next stories")])')
        if next_button_enabled:
            self.browser.click_element(
                f'(//button[contains(@aria-label, "Next stories")])')

    def excel_all_news(self) -> None:
        """Fetches all the news applying all the filters and exports them into excel sheet.
        """

        (headline_list,
         date_list,
         image_file_list,
         money_present_list,
         count_phrase_list) = self.get_data_lists()

        worksheet_data = {
            "Title": headline_list,
            "Date": date_list,
            "Image FileName": image_file_list,
            "Count of Search Phrase": count_phrase_list,
            "Money Present": money_present_list
        }

        self.excel.create_excel(worksheet_data, DIRECTORIES.FILEPATH)
