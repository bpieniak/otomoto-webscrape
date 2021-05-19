import pandas as pd
import glob
import argparse
from scrape_otomoto import scrape_otomoto
from translate import translate_pol_eng


def concat_scraped_data(scraped_folder):
    """
    concat scraped files into single dataframe
    """
    print("Concating scraped files..")
    scraped_paths = glob.glob(f"{scraped_folder}/*")
    all_offers = pd.DataFrame()
    for path in scraped_paths:
        curr_file = pd.read_csv(path)
        all_offers = pd.concat([all_offers, curr_file])

    all_offers.reset_index(drop=True, inplace=True)
    return all_offers


def cleanup(ds):
    ds = ds.drop(columns=['ID','URL'])

    # remove unit names and convert to numerical values
    ds['Przebieg'] = [None if str(mileage) == 'nan'
                        else int(mileage.replace("km", "").replace(" ", "")) for mileage in ds['Przebieg']]
    ds['Moc'] = [None if str(power) == 'nan'
                        else int(power.replace("KM", "").replace(" ", "")) for power in ds['Moc']]
    ds['Pojemność skokowa'] = [None if str(displacement) == 'nan'
                        else int(displacement.replace("cm3", "").replace(" ", "")) for displacement in ds['Pojemność skokowa']]
    ds['Emisja CO2'] = [None if str(emission) == 'nan'
                        else int(emission.replace("g/km", "").replace(" ", "")) for emission in ds['Emisja CO2']]

                        
    ds['Liczba drzwi'] = [None if str(door_num) == 'nan' else int(door_num) for door_num in ds['Liczba drzwi']]
    return ds 


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

    offers = cleanup(offers)

    if args.save_file:
        print("Saving to car_sale_ads_pol.csv")
        print(offers.keys())
        offers.to_csv("car_sale_ads_pol.csv", index_label="Index")

    if args.translate:
        print("Translating...")
        offers_eng = translate_pol_eng(offers)

        print("Saving to car_sale_ads.csv")
        print(offers_eng.keys())
        offers_eng.to_csv("car_sale_ads.csv", index_label="Index")