import pandas as pd
import numpy as np

import sys
sys.path.append('/mnt/')
from src.utils import (finder_natasha, find_postal_code)
from natasha import (
    MorphVocab,
    AddrExtractor,
)
from src.db_iface import PostgreIface

class AddrParser:
    """ 
    A class that processes `Справочник грузополучателей.xlsx` file 
    and parses addresses using various caches.

    Estimated working time:
    a) Using only caches and heuristics: time < 1 sec - O(1), coverage - 90.5% of addresses
    b) Additionally using a parser: time ~1-3 minutes - O(n)+network, coverage ~98% of addresses
    """

    def __init__(self, file_to_process: str):
        self.df: pd.DataFrame = self.read_buyer_excel(file_to_process)

        self.postgre = PostgreIface()
        self.morph_vocab = MorphVocab()
        self.addr_extractor = AddrExtractor(self.morph_vocab)
        
        self.cities, self.cities_set = self.fetch_cities()
        self.rzd_stations = self.fetch_stations()
        self.post_codes = self.fetch_post_codes()
        self.known = self.fetch_known_buyer()
    
    def read_buyer_excel(self, file_to_process: str = '/mnt/buyer.xlsx'):
        """ Function to read `Справочник грузополучателей.xlsx` file for future processing """

        df = pd.read_excel(file_to_process)
        df.columns = ['code', 'addr']
        df['geo'] = 'nan'
        df.code = df.code.astype(int)
        return df

    def fetch_cities(self):
        """ Read `cities` database """

        cities = self.postgre.read_table('cities')
        cities.city = cities.city.apply(lambda x: x.lower().replace('-','').replace(' ', ''))
        cities_set = set(cities.city)
        return cities, cities_set
    
    def fetch_stations(self):
        """ Read `rzd_stations` database """

        rzd_stations = self.postgre.read_table('rzd_stations')
        rzd_stations = rzd_stations.drop(rzd_stations[rzd_stations.code == 0].index).reset_index(drop=True)
        return rzd_stations

    def fetch_post_codes(self):
        """ Read `post_codes` database """

        post_codes = self.postgre.read_table('post_codes')
        post_codes.columns = list(map(str.lower, post_codes.columns.tolist()))
        post_codes = post_codes[['index', 'region', 'autonom', 'area', 'city', 'city_1', 'geo']]
        for col in ['region', 'autonom', 'area', 'city', 'city_1']:
            post_codes[col] = post_codes[col].apply(lambda x: x.lower() if isinstance(x, str) else None)
        post_codes.city = post_codes.city.apply(lambda x: x.lower().replace('-', '').replace(' ', '') if x is not None else '')
        return post_codes
    
    def fetch_known_buyer(self):
        """ Read `buyer` database """

        known = self.postgre.read_table('buyer')
        known.code = known.code.astype(int)
        return known

    def apply_buyer_cache(self):
        """ Applying a cache of known customer coordinates to the given table  """

        self.df['geo'] = self.df.code.apply(
            lambda x: self.known[self.known.code == x].geo.values[0] 
                    if x in self.known.code.values 
                    else 'nan'
        )
    
    def apply_cities_cache(self):
        """ Applying a cache of known cities coordinates to the given table  """

        self.df['geo'] = self.df.apply(
            lambda x: finder_natasha(x.addr, self.addr_extractor, self.cities, self.cities_set) 
                if x.geo == 'nan' 
                else x.geo, axis=1
        )
    
    def apply_postcodes_stations_cache_and_heuristics(self):
        """ 
        Applying a cache of known `post_codes` and `rzd_stations` coordinates.
        Applying heuristic methods.
        """

        for df_idx, (buyer_code, addr, geo) in zip(self.df[self.df.geo.isna()].index.tolist(), self.df[self.df.geo.isna()].values):
            some_pattern, mode = find_postal_code(addr)
            if (mode == 1) and (some_pattern != []):
                post_code = np.int64(some_pattern[0])
                if post_code in self.post_codes['index'].values:
                    self.df.loc[df_idx, 'geo'] = self.post_codes[self.post_codes['index'] == post_code].geo.values[0]
                elif post_code in self.rzd_stations.code.values:
                    self.df.loc[df_idx, 'geo'] = self.rzd_stations[self.rzd_stations.code == post_code].coords.values[0]

            elif (mode == 2) and (some_pattern != []):
                for some_pat in some_pattern:
                    station_code = np.int64(some_pat)
                    if station_code in self.rzd_stations.code.values:
                        self.df.loc[df_idx, 'geo'] = self.rzd_stations[self.rzd_stations.code == station_code].coords.values[0]
                        break
                for some_pat in some_pattern:
                    post_code = np.int64(some_pat)
                    if post_code in self.post_codes['index'].values:
                        self.df.loc[df_idx, 'geo'] = self.post_codes[self.post_codes['index'] == post_code].geo.values[0]
            elif "новый уренгой" in addr.lower():
                self.df.loc[df_idx, 'geo'] = '66.084539,76.680956'
            elif ("янао" in addr.lower()) or ('ямалоненец' in addr.lower()) or ('ямало-ненец' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = '66.529865,66.614507'
            elif 'лабытнанги' in addr.lower():
                self.df.loc[df_idx, 'geo'] = '66.660883,66.379930'
            elif 'усть-кут' in addr.lower():
                self.df.loc[df_idx, 'geo'] = '56.780882,105.745390'
            elif "тюменская обл" in addr.lower():
                self.df.loc[df_idx, 'geo'] = '57.152986,65.541231'
            elif "хмао" in addr.lower():
                self.df.loc[df_idx, 'geo'] = '61.003180,69.018902'
            elif ("база полярная" in addr.lower()) or ('полярная база' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = "70.280941,77.833787"
            elif ('ханты-манс' in addr.lower()) or ('ханты манс' in addr.lower()) or ('хантыманс' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = '61.003180,69.018902'
            elif ('ненецкий' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = '67.638050,53.006926'
            elif (' томск' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = '56.484645,84.947649'
            elif (' омск' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = '54.989347, 73.368221'
            elif ('ярославль' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = "57.626559,39.893813"
            elif 'ноябрьск' in addr.lower(): 
                self.df.loc[df_idx, 'geo'] = '63.201805,75.450938'
            elif 'архангельская обл' in addr.lower():
                self.df.loc[df_idx, 'geo'] = '64.539912,40.515762'
            elif "порт мурманск" in addr.lower():
                self.df.loc[df_idx, 'geo'] = '68.978908,33.067686'
            elif 'мегион' in addr.lower():
                self.df.loc[df_idx, 'geo'] = '61.032890,76.102621'
            elif ('заполярная' in addr.lower()) and ('база' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = '66.904119,78.914033'
            elif 'нурма' in addr.lower():
                self.df.loc[df_idx, 'geo'] = '56.708440,47.711348'
            elif 'морской порт' in addr.lower():
                self.df.loc[df_idx, 'geo'] = '59.911214,30.250741'
            elif 'саббета' in addr.lower():
                self.df.loc[df_idx, 'geo'] = '71.235938,72.127225'
            elif ('респ' in addr.lower()) and ('алтай' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = '51.957805,85.960631'
            elif ('респ' in addr.lower()) and ('беларусь' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = '53.902735,27.555691'
            elif ('москва' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = '55.755864,37.617698'
            elif ('спб' in addr.lower()) or ('санкт' in addr.lower()) or ('с-петерб' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = '59.938784,30.314997'
            elif ('тюменская' in addr.lower()) and ('обл' in addr.lower()):
                self.df.loc[df_idx, 'geo'] = '57.152986,65.541231'
            elif (mode == 3) and (some_pattern != []):
                if 'большой порт санкт' in addr.lower():
                    self.df.loc[df_idx, 'geo'] = '59.889584,30.209660'
            elif some_pattern == []:
                tokens = addr.lower().replace(',', ' ').replace('.', ' ').split()
                if ('ст' in tokens) and (tokens.index('ст') + 1 < len(tokens)):
                    station_name = tokens[tokens.index('ст') + 1].replace('-','')
                    if tokens[tokens.index('ст') + 1] in self.rzd_stations.station_name.values:
                        station_name = tokens[tokens.index('ст') + 1]
                        self.df.loc[df_idx, 'geo'] = self.rzd_stations[self.rzd_stations.station_name == station_name].coords.values[0]
                    elif (tokens.index('ст') + 2 < len(tokens)) and (station_name+tokens[tokens.index('ст') + 2] in self.rzd_stations.station_name.values):
                        station_name += tokens[tokens.index('ст') + 2]
                        self.rzd_stations[self.rzd_stations.station_name == station_name].coords.values[0]
                        self.df.loc[df_idx, 'geo'] = self.rzd_stations[self.rzd_stations.station_name == station_name].coords.values[0]

    def apply_selenium(self):
        """
        ! Функциональность не включена в решение !
        """
        pass

    def process(self):
        """ Main function """

        self.apply_buyer_cache()
        self.apply_cities_cache()
        self.apply_postcodes_stations_cache_and_heuristics()
        # self.apply_selenium() # UNCOMMENT IF IMPLEMENTED

        self.postgre.upd_buyers(self.df, self.known)
        return self.df


if __name__ == '__main__':
    file_to_parse = '/mnt/buyer.xlsx'
    parser = AddrParser(file_to_process=file_to_parse)
    tdf = parser.process()