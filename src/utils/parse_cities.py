import time
from pathlib import Path
from tqdm import tqdm
import time
from pathlib import Path
import pandas as pd
import seaborn as sns
from main_parser import GeoProcessor

sns.set(style='darkgrid')


if __name__ == '__main__':
    df = pd.read_csv('geodata/known_cities.csv')
    geopc = GeoProcessor()
    save_path = 'geodata/table_geo.csv'
    if not Path(save_path).exists():
        browser = geopc.init_browser_ymaps()
        for idx, (city, region, _) in tqdm(enumerate(df.values), total=df.shape[0]):
            addr = f'{city} {region}'
            result = geopc.process_v2(addr, browser)
            if isinstance(result, tuple):
                df.loc[idx, 'geo'] = ','.join(map(str, result))
            else:
                df.loc[idx, 'geo'] = str(result)
            if idx % 10 == 0:
                df.to_csv(save_path, index=False, encoding='UTF-8')
            if result in ['init', 'nan']:
                tqdm.write(f'{addr=}, {result=}')
            time.sleep(2)
