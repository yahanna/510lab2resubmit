# Techin510-lab2
Web Scraper

## Overview
This Python script is designed for extracting event information from visitseattle.com and augmenting this data with weather forecasts based on the event's location and date.

## Requirements
- Python 3.x
- Libraries: `requests`, `bs4` (BeautifulSoup), `csv`


```bash
pip install -r requirements.txt
python main.py
```
## Lessons Learned

### 1. Error Handling and Data Validation

- The development process highlighted the criticality of implementing robust error handling mechanisms, especially when dealing with web scraping and external API requests. Unexpected data formats, network issues, or changes in the structure of the target webpage can lead to exceptions that need to be handled gracefully.

### 2. Dynamic Data Handling

- The project involved navigating through multiple pages of a website (pagination) to collect comprehensive data. This experience underscored the importance of efficiently handling dynamic web content and the need for scripts to adapt to varying amounts of data across different pages.

## Questions

- How can the web scraper be adapted to handle changes in the website's layout or structure to ensure long-term reliability?
- What are the possible ways to scale the scraper to handle a larger number of pages or multiple websites without significantly increasing resource usage?
