import pandas as pd
import pickle
import re

def load_pkl(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


def translate_car_features(features_string):
    car_features_translation = load_pkl("./translation_files/car_features_translation")
    features = re.findall(r"\'(.*?)\'", features_string)

    translated_features = list()
    for feature in features:
        if feature:
            translation = car_features_translation[feature]
            translated_features.append(translation)

    return translated_features


def translate_pol_eng(dataframe):
    """
    """
    key_translation = load_pkl("./translation_files/key_translation")
    colour_translation = load_pkl("./translation_files/colour_translation")
    fuel_type_translation = load_pkl("./translation_files/fuel_type_translation")
    drive_translation = load_pkl("./translation_files/drive_translation")
    transmission_translation = load_pkl("./translation_files/transmission_translation")
    type_translation = load_pkl("./translation_files/type_translation")
    colour_translation = load_pkl("./translation_files/colour_translation")
    origin_country_translation = load_pkl("./translation_files/origin_country_translation")

    dataframe.rename(mapper=key_translation, axis=1, inplace=True)
    dataframe.Vehicle_model.replace({"Inny":"Other"}, inplace=True)
    dataframe.Vehicle_version.replace({"Inny":"Other"}, inplace=True)
    dataframe.Condition.replace(colour_translation, inplace=True)
    dataframe.Fuel_type.replace(fuel_type_translation, inplace=True)
    dataframe.Drive.replace(drive_translation, inplace=True)
    dataframe.Transmission.replace(transmission_translation, inplace=True)
    dataframe.Type.replace(type_translation, inplace=True)
    dataframe.Colour.replace(colour_translation, inplace=True)
    dataframe.Origin_country.replace(origin_country_translation, inplace=True)
    dataframe.Features = dataframe.Features.apply(translate_car_features)
    return dataframe