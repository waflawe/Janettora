import asyncio
import sys
import typing
from importlib import import_module
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup
from loguru import logger

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

utils = import_module("database.utils")
models = import_module("database.models")

logger.add(".logs/parser.log", level="INFO")

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-A217F Build/RP1A.200720.012; wv) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.91 Mobile Safari/537.36"
}

WORDERDICT_DOMAIN = "https://www.worderdict.ru"
DEFAULT_WORDERDICT_PARSE_URL = WORDERDICT_DOMAIN + "/words/"


class WorderdictParser(object):
    @classmethod
    def configure(cls, url: str, headers: typing.Optional[typing.Mapping] = None) -> None:
        """
        Configure the parser.

        :param url: Worderdict url to parse.
        :param headers: Headers used for url requests.
        """

        cls.url = url
        cls.headers = headers or DEFAULT_REQUEST_HEADERS
        cls.counter = cls.pages_counter = 0
        cls.valid_part_of_speech_values = models.WordPartsOfSpeech.get_valid_values()

    async def parse(self) -> None:
        """Start parsing."""

        logger.info(f"Начало парсинга {self.url} домена.")
        pages_count = await self.get_pages_count()
        logger.info(f"{pages_count} Страниц будут выпотрошены (около {pages_count*25} слов).")
        await self.parse_many_pages(pages_count)
        logger.info("Окончание парсинга.")

    async def get_soup(self, url: typing.Optional[str] = None) -> BeautifulSoup:
        """
        Get BeautifulSoup object for url.

        :param url: Requested url.
        :return: BeautifulSoup object with the content obtained from the url.
        """

        async with aiohttp.ClientSession() as session:
            response = await session.get(url if url else self.url, headers=self.headers)
            soup = BeautifulSoup(await response.text(), "lxml")
            return soup

    async def get_pages_count(self) -> int:
        """
        Get count of pages

        :return: Count of pages by configured url.
        """

        soup = await self.get_soup()
        return int(
            soup
            .find("div", class_="w-full flex flex-row justify-center my-2")
            .find_all("a")[-1]
            .text
        )

    async def parse_many_pages(self, count: int) -> None:
        """
        Start parse pages.

        :param count: Number of pages to be parsed.
        """

        tasks = []

        for page in range(0, count):
            task = asyncio.create_task(self.parse_page(page))
            tasks.append(task)

        await asyncio.gather(*tasks)

        if self.pages_counter % 100 != 0:
            logger.info(f"Выпотрошено {self.pages_counter} страниц ({self.counter} слов).")

    async def parse_page(self, page: int) -> None:
        """
        Parse one page and insert parsed data to database.

        :param page: Number of page that will be parsed.
        """

        soup = await self.get_soup(self.url + f"?page={page}")
        self.pages_counter += 1
        try:
            all_cards = (
                soup
                .find("div", class_="w-full lg:w-4/5")
                .find_all("div", class_="py-2 lg:py-4")
            )
        except AttributeError:
            logger.info(f"Парсер был забанен! Текущие счетчики: {self.pages_counter} страниц, {self.counter} слов.")
            quit(0)

        for card in all_cards:
            word_attributes = (
                await self.get_and_validate_english(card),
                await self.get_and_validate_russian(card),
                await self.get_and_validate_part_of_speech(card)
            )
            if all(word_attributes):
                utils.create_word(*word_attributes)
                self.counter += 1

        if self.pages_counter % 100 == 0:
            logger.info(f"Выпотрошено {self.pages_counter} страниц ({self.counter} слов).")

    async def get_and_validate_english(self, card: BeautifulSoup) -> str | None:
        return (
            card
            .find("div", class_="w-full mb-3 lg:mb-0 relative")
            .find("h3", class_="card-title")
            .text
        )

    async def get_and_validate_russian(self, card: BeautifulSoup) -> str | None:
        try:
            russian = (
                card
                .find_all("div", class_="w-full")[-1]
                .find_all("a", lang="ru")[0]
                .text
            )
        except IndexError:
            return None
        if "\n" not in russian:
            return russian
        return None

    async def get_and_validate_part_of_speech(self, card: BeautifulSoup) -> str | None:
        try:
            part_of_speech = (
                card
                .find("div", class_="pb-1")
                .text
            )
        except AttributeError:
            return None
        part_of_speech = "_".join(part_of_speech.lower().split(" "))

        if part_of_speech in self.valid_part_of_speech_values:
            return part_of_speech
        return None


def main() -> None:
    utils.destroy_word_model(), utils.create_word_model()

    WorderdictParser.configure(DEFAULT_WORDERDICT_PARSE_URL)
    p = WorderdictParser()
    asyncio.run(p.parse())


if __name__ == "__main__":
    main()
