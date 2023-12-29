from rutpy import generate as generate_rut
from unidecode import unidecode
import gender_guesser.detector as gender
import dateparser

import re
import random
import os
import csv
from datetime import datetime, timedelta
from dataclasses import dataclass
from sys import stderr

male_names_location = os.environ['MALE_NAMES']
female_names_location = os.environ['FEMALE_NAMES']
last_names_location = os.environ['LAST_NAMES']

occupation_location = os.environ['OCCUPATION']
company_location = os.environ['COMPANY']
health_care_unit_location = os.environ['HEALTH_CARE_UNIT']

location_location = os.environ['LOCATION']
town_location = os.environ['TOWN']
city_location = os.environ['CITY']
region_location = os.environ['REGION']
street_location = os.environ['STREET']
comuna_location = os.environ['COMUNA']
neighborhood_location = os.environ['NEIGHBORHOOD']

ignored_entities = set(os.environ.get('IGNORED', '').split(','))

providers = ['gmail', 'hotmail', 'outlook']

days_of_week = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
days_of_week_set = {'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'}

with open(male_names_location, 'r') as f:
    MALE_NAMES = [line.strip() for line in f]
with open(female_names_location, 'r') as f:
    FEMALE_NAMES = [line.strip() for line in f]
with open(last_names_location, 'r') as f:
    LAST_NAMES = [line.strip() for line in f]

with open(town_location, 'r') as f:
    TOWNS = [line.strip() for line in f]
with open(city_location, 'r') as f:
    CITIES = [line.strip() for line in f]
with open(region_location, 'r') as f:
    REGIONS = [line.strip() for line in f]
with open(street_location, 'r') as f:
    STREETS = [line.strip() for line in f]
with open(comuna_location, 'r') as f:
    COMUNAS = [line.strip() for line in f]
with open(neighborhood_location, 'r') as f:
    NEIGHBORHOODS = [line.strip() for line in f]

location_map = {
    'town': TOWNS,
    'city': CITIES,
    'region': REGIONS,
    'street': STREETS,
    'comuna': COMUNAS,
    'neighborhood': NEIGHBORHOODS
}

with open(occupation_location, 'r') as f:
    reader = csv.DictReader(f)
    OCCUPATIONS = {unidecode(r['occupation'].lower()): r['mapped'] for r in reader if r['mapped'].strip()}
with open(company_location, 'r') as f:
    reader = csv.DictReader(f)
    COMPANIES = {unidecode(r['company'].lower()): r['mapped'] for r in reader if r['mapped'].strip()}
with open(location_location, 'r') as f:
    reader = csv.DictReader(f)
    LOCATIONS = {unidecode(r['location'].lower()): r['mapped'] for r in reader if r['mapped'].strip()}
with open(health_care_unit_location, 'r') as f:
    reader = csv.DictReader(f)
    HEALTH_CARE_UNITS = {unidecode(r['unit'].lower()): r['mapped'] for r in reader if r['mapped'].strip()}

age_re = re.compile(r'[0-9]+')
d = gender.Detector()

@dataclass
class Configuration:
    debug: bool = False
    tolerate_unhandled: bool = False

CONFIG = Configuration()

def debug(msg):
    if CONFIG.debug:
        print(msg, file=stderr)

def pseudonymize(text, label) -> str:
    case = infer_case(text.strip())

    match label:
        case 'Age':
            replaced = age(text)
        case 'Phone_Number':
            replaced = phone_number()
        case 'RUT':
            replaced = rut()
        case 'IDs':
            replaced = ids(text)
        case 'First_Name':
            replaced = first_name(text)
        case 'Last_Name':
            replaced = last_name()
        case 'Date_Part':
            replaced = date(text)
        case 'Full_Date':
            replaced = date(text)
        case 'Company':
            replaced = company(text)
        case 'Location':
            replaced = location(text)
        case 'Health_Care_Unit':
            replaced = health_care_unit(text)
        case 'Occupation':
            replaced = occupation(text)
        case 'Email':
            replaced = email()

        case other:
            if other in ignored_entities:
                return text
            elif CONFIG.tolerate_unhandled:
                debug(f'[Warning] Pseudonymizer was fed "{text}" with the unhandled label "{other}".')
                return text
            else:
                raise ValueError(f'Pseudonymizer was fed "{text}" with the unhandled label "{other}"')
    
    match case:
        case 'LOWER':
            return replaced.lower()
        case 'UPPER':
            return replaced.upper()
        case 'CAPITALIZED':
            return replaced.capitalize()

def infer_case(text: str):
    if text.islower():
        return 'LOWER'
    elif text.isupper():
        return 'UPPER'
    elif all(not s.isalpha() for s in text):
        return 'CAPITALIZED'
    else:
        return 'CAPITALIZED'

def age(text) -> str:
    age_candidates = [int(age_text) for age_text in age_re.findall(text)]
    if len(age_candidates) < 1:
        raise ValueError(f'Age annotation does not contain a number: {text}')

    age_candidates = sorted(age_candidates, key=lambda age: abs(age - 20))
    age = age_candidates[0]

    return f'{max(age + random.randint(-5, 5), 18)} años'

def phone_number() -> str:
    digits = [str(random.randint(0, 9)) for _ in range(8)]
    new_number = f'9{"".join(digits)}'

    return new_number

def rut() -> str:
    return generate_rut()[0]

def ids(text) -> str:
    text = unidecode(text.lower().strip())
    parts = []
    for c in text:
        if c.isalpha():
            parts.append(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        elif c in '1234567890':
            parts.append(str(random.randint(0, 9)))
        else:
            parts.append(c)
    
    return ''.join(parts)

def first_name(text) -> str:
    gender = d.get_gender(text.strip())

    if gender in ('male', 'mostly_male'):
        random.shuffle(MALE_NAMES)
        name_list = MALE_NAMES
    elif gender in ('female', 'mostly_female'):
        random.shuffle(FEMALE_NAMES)
        name_list = FEMALE_NAMES
    else:
        random.shuffle(MALE_NAMES)
        random.shuffle(FEMALE_NAMES)
        name_list = MALE_NAMES + FEMALE_NAMES

    return name_list[0]


def last_name() -> str:
    random.shuffle(LAST_NAMES)
    name_list = LAST_NAMES

    return name_list[0]

def date(text) -> str:
    text = unidecode(text.lower().strip())
    if text in 'lmjvsd' or text in days_of_week_set:
        text = random.sample(days_of_week, k=1)[0]

    if not (dt := dateparser.parse(text)):
        year_delta = random.randint(-3, 3)
        month = random.randint(1, 12)
        day = random.randint(1, 28 if month == 2 else 31 if month in {1, 3, 5, 7, 8, 10, 12} else 30)
        return datetime(2020 + year_delta, month, day).strftime('%m/%d/%Y')
    
    else:
        new_date = dt + timedelta(random.randint(-3, 3))
        new_date = datetime(2020 + random.randint(-3, 3), month=new_date.month, day=new_date.day)

        return new_date.strftime('%m/%d/%Y')

def company(text) -> str:
    text = unidecode(text.lower().strip())
    try:
        replacement = COMPANIES[text]
        if replacement == 'full_name':
            replacement = f'{first_name("N/A")} {last_name()}'
        if replacement == 'occupation':
            replacement = occupation('N/A')
    except KeyError:
        debug(f'[Warning] Company "{text}" did not have a mapping.')
        replacement = 'una empresa'

    return replacement

def location(text) -> str:
    text = unidecode(text.lower().strip())
    try:
        category = LOCATIONS[text]
        replacement = random.sample(location_map[category], k=1)[0]
    except KeyError:
        debug(f'[Warning] Location "{text}" did not have a mapping.')
        replacement = 'un lugar'

    return replacement

def health_care_unit(text) -> str:
    text = unidecode(text.lower().strip())
    try:
        replacement = HEALTH_CARE_UNITS[text]
    except KeyError:
        debug(f'[Warning] Health care unit "{text}" did not have a mapping.')
        replacement = 'un hospital'

    return replacement

def occupation(text) -> str:
    text = unidecode(text.lower().strip())
    try:
        replacement = OCCUPATIONS[text]
    except KeyError:
        debug(f'[Warning] Occupation "{text}" did not have a mapping.')
        replacement = 'trabajador'

    return replacement

def email() -> str:
    random.shuffle(providers)
    return f'{first_name("N/A")}.{last_name()}@{providers[0]}.com'