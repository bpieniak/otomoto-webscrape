# Otomoto webscrape

Script webscraping car offers from car advertisement site [Otomoto.pl](https://www.otomoto.pl/).

Script used to collect data for [Kaggle dataset](https://www.kaggle.com/bartoszpieniak/poland-cars-for-sale-dataset).

Use only when you have enough time. For full scrape you need few hours.

### Usage
- Example:

		$ python3.py main.py [options]
	
- Option description:  

		--scraped_data 	Folder containing scraped data. Use if already run webscraped (default: None - will run webscraping script)
		--save_file 		Save file with polish names (default=True)
		--translate 		Translate to english and save the file (default=True)
