# -*- coding: utf-8 -*-
import requests
import json
import time
import os
from csv import DictReader
from datetime import datetime, date, timedelta


LANGS = ["fr", "es", "en", "de"]


def readCsv(name, mapping, myKey="code"):
    the_reader = DictReader(open(name, 'r', encoding="utf8"))
    output = [{key: _[value] for key, value in mapping.items()}
              for _ in the_reader]
    return {_[myKey]: {k: v for k, v in _.items() if k != myKey} for _ in output}


def merge(mainDict, dictsToBeMerged):
    output = []
    for k, _ in mainDict.items():
        for toBeMerged in dictsToBeMerged:
            el = toBeMerged.get(k)
            if el:
                for key, value in el.items():
                    _[key] = value
        output.append({**_, **{"code": k}})
    return output


def readCountries(myKey="code"):
    return readCsv("countries.csv", {
        "code": "iso3",
        "country_en": "country_en",
        "country_fr": "country_fr",
        "country_es": "country_es",
        "country_de": "country_de",
        "continent_en": "continent_en",
        "continent_fr": "continent_fr",
        "continent_es": "continent_es",
        "continent_de": "continent_de"
    }, myKey=myKey)


def retrieveRawData():
    areas = readCsv("countries_area.csv", {
        "code": "Country Code",
        "area": "2018"
    })

    populations = readCsv("population.csv", {
        "code": "Country_Code",
        "population": "Year_2016"
    })

    countries = readCsv("countries.csv", {
        "code": "iso3",
        "country_en": "country_en",
        "country_fr": "country_fr",
        "country_es": "country_es",
        "country_de": "country_de",
        "continent_en": "continent_en",
        "continent_fr": "continent_fr",
        "continent_es": "continent_es",
        "continent_de": "continent_de"
    })

    countriesMeta = merge(countries, [areas, populations])
    countriesMetaByFrance = {_["country_fr"]: _ for _ in countriesMeta}

    with open("data.json", "r") as f:
        d = json.loads(f.read())

    covid19data = []
    for row in d["GlobalData"]:
        for _ in countries["FRA"].keys():
            row[_] = None
        row["code"] = None
        covid19data.append(row)
    for row in d["PaysData"]:
        meta = countriesMetaByFrance.get(row["Pays"])
        if meta:
            row = {**row, **meta}
        else:
            for _ in countries["FRA"].keys():
                row[_] = None
        covid19data.append(row)

    pivotedOutput = []
    mapping = {
        "Date": "date",
        "Pays": "country_name",
        "code": "country_code",
        "Deces": "dead",
        "Guerisons": "healed",
        "TauxDeces": "death_rate",
        "TauxGuerison": "heal_rate",
        "Infection": "infected",
        "TauxInfection": "infected_rate",
    }
    for row in covid19data:
        for lang in LANGS:
            o = {}
            for key, value in row.items():
                if key.endswith("_"+lang):
                    o[key.replace("_"+lang, "")] = value
                elif "_" not in key:
                    new_key = mapping.get(key, key)
                    o[new_key] = value if new_key != "date" else datetime.strptime(
                        value, "%Y-%m-%dT00:00:00")
                    # o[new_key] = float(o[new_key])
                    if new_key in ["population", "area"]:
                        try:
                            o[new_key] = int(o[new_key])
                        except:
                            o[new_key] = None
            o["lang"] = lang
            pivotedOutput.append(o)

    return pivotedOutput


def getDates():
    edate = date.today()
    sdate = date(2020, 3, 19)
    delta = edate - sdate

    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        s = day.strftime("%m-%d-%Y")
        r = requests.get("https://covid19.mathdro.id/api/daily/"+s)
        jsonResponse = json.loads(r.text)
        with open("daily/"+s+".json", "w") as f:
            f.write(json.dumps(jsonResponse))
        time.sleep(0.5)


def scanDailyFolder():
    folder = "daily"
    o = {}
    mapping = {
        "Reunion": "Réunion",
        "Congo (Kinshasa)": "Congo - Kinshasa",
        "US": "United States",
        "Mainland China": "China",
        "UK": "United Kingdom",
        "Korea, South": "South Korea",
        "Republic of Ireland": "Ireland",
        "Republic of Korea": "North Korea",
        "Russian Federation": "Russia",
        "Viet Nam": "Vietnam",
        "Taiwan*": "Taiwan",
        "Taipei and environs": "Taiwan",
        "Cote d'Ivoire": "Ivory Coast",
        " Azerbaijan": "Azerbaijan",
        "Saint Martin": "Sint Maarten",
        "Bosnia and Herzegovina": "Bosnia & Herzegovina",
        "St. Martin": "Sint Maarten",
        "Republic of Moldova": "Moldova",
        "Iran (Islamic Republic of)": "Iran",
        "North Ireland": "United Kingdom",
        "Hong Kong SAR": "China",
        "Macao SAR": "China",
        "North Macedonia": "Macedonia (FYROM)",
        "Czech Republic": "Czechia"
    }
    notFound = set()
    mapCountries = readCountries(myKey="country_en")
    mapCountryCode = readCountries()
    mapPopulation = readCsv("population.csv", {
        "code": "Country_Code",
        "population": "Year_2016"
    })
    mapArea = readCsv("countries_area.csv", {
        "code": "Country Code",
        "area": "2018"
    })

    # for key, value in mapCountries:
    #     print(value["country_fr"])
    used = set()
    output = []
    newMap = {}
    lat_lngs = {}
    for filename in os.listdir(folder):
        with open(os.path.join(folder, filename)) as f:
            countries = json.loads(f.read())
            newMap[filename] = {}
            for c in countries:
                el = c["countryRegion"]
                if not mapCountries.get(c["countryRegion"]):
                    if mapping.get(c["countryRegion"]):
                        el = mapping.get(c["countryRegion"])
                        if not mapCountries.get(el):
                            notFound.add(c["countryRegion"])
                        else:
                            used.add(c["countryRegion"])
                    else:
                        notFound.add(c["countryRegion"])
                else:
                    used.add(c["countryRegion"])
                if el and mapCountries.get(el):
                    o = mapCountries.get(el)
                    code = o["code"]
                    lat_lngs[code] = lat_lngs.get(
                        code, {"count": 0, "lat": 0, "lng": 0})
                    newMap[filename][code] = newMap[filename].get(code, {})
                    for l in ["deaths", "confirmed", "recovered"]:
                        if c.get(l):
                            newMap[filename][code][l] = newMap[filename][code].get(
                                l, 0) + int(c[l])
                    if "latitude" in c.keys() and "longitude" in c.keys():
                        lat_lngs[code]["count"] += 1
                        lat_lngs[code]["lat"] += float(c["latitude"])
                        lat_lngs[code]["lng"] += float(c["longitude"])
                    newMap[filename][code]["count"] = newMap[filename][code].get(
                        "count", 0) + 1
                    newMap[filename][code] = {**newMap[filename][code], **o}
    output = []
    for date, value in newMap.items():
        date = date.replace(".json", "")
        date = datetime.strptime(date, '%m-%d-%Y').strftime('%Y-%m-%d')
        for country_code, value2 in value.items():
            output.append({**value2, "date": date, "country_code": country_code,
                           "country_en": mapCountryCode[country_code]["country_en"]})

    for k, v in lat_lngs.items():
        v["lat"] = v["lat"] / v["count"]
        v["lng"] = v["lng"] / v["count"]
        del v["count"]
    output2 = []
    for val in output:
        val = {**val, **lat_lngs[val["country_code"]],
               "area": mapArea.get(val["country_code"], {"area": None})["area"],
               "pop": mapPopulation.get(val["country_code"], {'population': None})["population"]}
        val["code"] = val["country_code"]
        val = {k: v for k, v in val.items() if k not in [
            "latitude", "longitude", "country_code"]}
        output2.append(val)

    output = sorted(output2, key=lambda x: x["date"])

    with open("./covid19/public/data.json", "w") as f:
        f.write(json.dumps(output))
    with open("./covid19/public/countries.json", "w") as f:
        f.write(json.dumps(mapCountryCode))


if __name__ == "__main__":
    getDates()
    scanDailyFolder()
