import scrapy
from scrapy.crawler import CrawlerProcess
from pathlib import Path
import os

class VoteSpider(scrapy.Spider):
    name = 'vote_spider'

    def __init__(self, start_year, end_year, *args, **kwargs):
        super(VoteSpider, self).__init__(*args, **kwargs)
        self.start_year = int(start_year)
        self.end_year = int(end_year)
        self.base_url = 'https://clerk.house.gov/Votes/{}{:04d}'

    def start_requests(self):
        for year in range(self.start_year, self.end_year + 1):
            yield from self.crawl_year(year)

    def crawl_year(self, year):
        vote_number = 1
        while True:
            url = self.base_url.format(year, vote_number)
            yield scrapy.Request(url, callback=self.parse, meta={'year': year, 'vote_number': vote_number})
            vote_number += 1

    def parse(self, response):
        year = response.meta['year']
        vote_number = response.meta['vote_number']

        base_folder = Path("vote_records")
        year_folder = base_folder / str(year)
        file_name = f"{year}_{vote_number:04d}.html"
        file_path = year_folder / file_name

        if response.status == 200:
            if "Roll call vote not available" in response.text:
                self.logger.info(f"Finished year {year} at vote number {vote_number - 1}")
                return  # This will stop the crawling for the current year

            year_folder.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(response.body)
            
            self.logger.info(f"Saved: {file_path}")
            yield {'url': response.url, 'file': str(file_path)}
        else:
            self.logger.info(f"Skipping vote {vote_number} for year {year} due to non-200 status")
            if vote_number > 1000:  # Arbitrary large number to prevent infinite loop
                self.logger.info(f"Reached vote number 1000 for year {year}, moving to next year")
                return

# Run the spider
if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'CONCURRENT_REQUESTS': 16,  # Adjust based on your needs and respect for the website
        'DOWNLOAD_DELAY': 1,  # Be polite, add a delay between requests
    })

    process.crawl(VoteSpider, start_year=2010, end_year=2024)
    process.start()
