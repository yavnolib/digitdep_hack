import string
import re

IGNORED_WORDS = {"Россия", "РФ", "ХМАО", "ЯНАО", "МО"}

def find_postal_code(address: str) -> str | None:
    # Регулярное выражение для поиска 6-значных чисел
    pattern = r'\b\d{6}\b'
    candidates = re.findall(pattern, address)

    st_pattern = r'\bст\.\b'
    station_pattern_i = r'\bстанция\b'
    station_pattern_ii = r'\bст\b'
    station_pattern_iii = r'\bстанции\b'
    station_pattern_iv = r'\bж\/д\b'
    port_pattern = r'\bпорт\b'

    st_dol_patter = r'\bкод\d{6}\b'
    if (not re.search(st_pattern, address)) and (not re.search(station_pattern_i, address)) and (not re.search(station_pattern_ii, address)) and (not re.search(station_pattern_iii, address)) and (not re.search(station_pattern_iv, address)):
            return [candidate for candidate in candidates], 1
    elif re.search(st_dol_patter, address):
        station_candidates = re.findall(st_dol_patter, address)
        return [candidate.split('код')[1] for candidate in station_candidates], 2
    elif (re.search(st_pattern, address)) or (re.search(station_pattern_i, address)) or (re.search(station_pattern_ii, address)) or (re.search(station_pattern_iii, address)) or (re.search(station_pattern_iv, address)):
        station_candidates_pattern = r'\b\d{5}\b'
        station_candidates = re.findall(station_candidates_pattern, address)
        return [candidate for candidate in candidates] + [candidate for candidate in station_candidates], 2
    elif re.search(port_pattern, address):
         return 'порт', 3
    return 0

def apply_finder(x, cities, cities_set):
    c_id, list_r = clear_addr(x.lower())
    if c_id + 1 < len(list_r):
        town = list_r[c_id + 1]
    else:
        town = 'nan'
    if town in cities_set:
        return cities.query(f'city == "{town}"').geo.values[0]
    else:
        return 'nan'


def finder_natasha(x, addr_extractor, cities, cities_set):
    matches = addr_extractor(x)
    town = 'nan'
    for match in matches:
        if match.fact.type == 'город':
            town = match.fact.value
            break
    if town.lower() in cities_set:
        res = cities.query(f'city == "{town.lower()}"').geo.values
        if res.shape[0] > 1:
            return 'nan'
        return res[0]

def extract_city(address):
    city_pattern = (
        r'\b(?:г\.|город\s+)?'
        r'([А-ЯЁ][а-яё\-]+(?:\s+[А-ЯЁ][а-яё\-]+)*)'
        r'\b'
    )
    
    matches = re.findall(city_pattern, address)
    filtered_matches = [m for m in matches if m not in IGNORED_WORDS]
    return filtered_matches[0] if filtered_matches else None

def custom_strip(text):
    strip_chars = string.whitespace + string.punctuation
    return text.strip(strip_chars)

def clear_addr(addr):
    addr = addr.lower() if isinstance(addr, str) else addr
    list_r = list(map(custom_strip, addr.replace('город', 'г.').replace(',', ' ').replace('.', ' ').split()))
    if 'г' in list_r:
        res_idx = list_r.index('г')
    else:
        res_idx = 1
    return res_idx, list_r