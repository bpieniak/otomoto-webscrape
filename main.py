import pandas as pd
import glob
import argparse
from scrape_otomoto import scrape_otomoto
from translate import translate_pol_eng


def concat_scraped_data(scraped_folder):
    """
    concat scraped files into single dataframe
    """
    scraped_paths = glob.glob(f"{scraped_folder}/*")
    all_offers = pd.DataFrame()
    for path in scraped_paths:
        curr_file = pd.read_csv(path)
        all_offers = pd.concat([all_offers, curr_file])

    return all_offers


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--scraped_data', default=None, type=str,
                        help='Folder containing scraped data. Default: None - will run webscraping script.')
    parser.add_argument('--save_file', default=True, type=bool,
                        help='Translate the file.')
    parser.add_argument('--translate', default=True, type=bool,
                        help='Translate and save the file.')
    args = parser.parse_args()

    if not args.scraped_data:
        scrape_otomoto()
        offers = concat_scraped_data("./scraped_data")
    else:
        offers = concat_scraped_data(args.scraped_data)

    if args.save_file:
        offers.to_csv("car_sale_ads_pol.csv")

    if args.translate:
        offers_eng = translate_pol_eng(offers)
        offers_eng.to_csv("car_sale_ads.csv")