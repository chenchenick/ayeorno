import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from pathlib import Path
import re
from scrapy.exceptions import CloseSpider

class YearVoteSpider(scrapy.Spider):
    name = 'year_vote_spider'

    def __init__(self, year, *args, **kwargs):
        super(YearVoteSpider, self).__init__(*args, **kwargs)
        self.year = int(year)
        self.base_url = 'https://clerk.house.gov/Votes/{}{:04d}'
        self.base_folder = Path("vote_records")
        self.downloaded_votes = self.collect_downloaded_votes()

    def start_requests(self):
        vote_number = 1
        while vote_number <= 1000:  # Limit to prevent infinite loop
            if vote_number in self.downloaded_votes:
                self.logger.info(f"Skipping already downloaded vote {vote_number} for year {self.year}")
                vote_number += 1
                continue
            
            url = self.base_url.format(self.year, vote_number)
            yield scrapy.Request(url, callback=self.parse, meta={'vote_number': vote_number})
            vote_number += 1

    def collect_downloaded_votes(self):
        downloaded = set()
        year_folder = self.base_folder / str(self.year)
        if year_folder.is_dir():
            for file in year_folder.glob("*.html"):
                match = re.match(r"(\d+)_(\d+)\.html", file.name)
                if match:
                    vote_number = int(match.group(2))
                    downloaded.add(vote_number)
        return downloaded

    def parse(self, response):
        vote_number = response.meta['vote_number']

        year_folder = self.base_folder / str(self.year)
        file_name = f"{self.year}_{vote_number:04d}.html"
        file_path = year_folder / file_name

        if response.status == 200:
            if "Roll call vote not available" in response.text:
                self.logger.info(f"No more votes available for year {self.year} after vote number {vote_number - 1}")
                raise CloseSpider(f"Finished crawling votes for year {self.year}")

            year_folder.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(response.body)
            
            self.logger.info(f"Saved: {file_path}")
            yield {'url': response.url, 'file': str(file_path)}
        else:
            self.logger.info(f"Skipping vote {vote_number} for year {self.year} due to non-200 status")

def run_spiders(start_year, end_year):
    settings = get_project_settings()
    settings.update({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'CONCURRENT_REQUESTS': 1,  # Process one request at a time per spider
        'DOWNLOAD_DELAY': 1,  # Be polite, add a delay between requests
        'LOG_LEVEL': 'INFO',  # To see more detailed output
        'ROBOTSTXT_OBEY': False,  # We're not obeying robots.txt in this case
    })

    process = CrawlerProcess(settings)

    years = list(range(start_year, end_year + 1))
    
    for year in years:
        process.crawl(YearVoteSpider, year=year)
    
    process.start()  # This will block until all spiders are finished

if __name__ == "__main__":
    run_spiders(start_year=2010, end_year=2024)
