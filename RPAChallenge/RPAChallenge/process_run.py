import os
import shutil

from filepaths import DIRECTORIES
from logger import logger
from Reuters import NewsFromReuters


class Process:
    def __init__(self, workitems: dict) -> None:
        self.workitems = workitems

    def make_dirs(self) -> None:
        """
        Builds required directories.
        """
        if not os.path.exists(DIRECTORIES.OUTPUT):
            os.mkdir(DIRECTORIES.OUTPUT)
        if not os.path.exists(DIRECTORIES.IMAGE_PATH):
            os.mkdir(DIRECTORIES.IMAGE_PATH)

    def run_process(self):
        """Runs the entire process for fetching the required news data.
        """
        try:
            news = NewsFromReuters(self.workitems)

            logger.info("Opens the webpage from the news website: Reuters.")
            news.open_website()
            logger.info("Website successfully opened.")

            news_available, message = news.check_news_data_present()
            logger.info("Successfully checked for news search results.")

            if news_available:
                try:
                    logger.info("Initialising the uploading of news data.")
                    news.excel_all_news()
                    logger.info(
                        "Required news fetched successfully in the excel.")
                    logger.info("Ending the process.")
                    shutil.make_archive(DIRECTORIES.ARCHIVES_PATH,
                                        'zip', DIRECTORIES.IMAGE_PATH)
                    shutil.rmtree(DIRECTORIES.IMAGE_PATH)

                except:
                    logger.info(message)
                    logger.info("Ending the process.")

        except Exception as e:
            news.browser.screenshot(
                filename=DIRECTORIES.ERROR_SCREENSHOT_PATH)
            raise e

    def start(self):
        """Starts process.
        """
        self.make_dirs()
        self.run_process()
