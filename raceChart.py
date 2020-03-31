# -*- coding: utf-8 -*-
import json
import os
all_measures = ["deaths", "recovered",
                "confirmed", "confirmed_deaths_recovered",
                "deaths_pop", "deaths_area",
                "recovered_pop", "recovered_area",
                "confirmed_pop", "confirmed_area",
                "confirmed_deaths_recovered_pop", "confirmed_deaths_recovered_area"]

PATH = "./covid19/public/"

measure_country_date = {}
dates = []
countries = []


def getMeasure(row, m):
    if "_" not in m:
        return int(row.get(m, 0))
    arr = m.split("_")
    if len(arr) == 3:
        return int(row.get(arr[0], 0) - row.get(arr[1], 0) - row.get(arr[2], 0))
    if len(arr) == 2:
        if row.get(arr[1], 0) == 0 or row[arr[1]] == None or row[arr[1]] == "":
            return 0
        return int(row.get(arr[0], 0)) / float(row[arr[1]])
    if len(arr) == 4:
        if row.get(arr[-1], 0) == 0 or row[arr[-1]] == None or row[arr[-1]] == "":
            return 0
        return (int(row.get(arr[0], 0) - row.get(arr[1], 0) - row.get(arr[2], 0))) / float(row[arr[-1]])


def createRace():
    with open(PATH + "data.json") as f:
        data = json.loads(f.read())
        dates = set([_["date"] for _ in data])
        dates = sorted(dates)
        countries = set([_["code"] for _ in data])

        for row in data:
            for m in all_measures:
                measure_country_date[m] = measure_country_date.get(m, {})
                measure_country_date[m][row["code"]
                                        ] = measure_country_date[m].get(row["code"], {})
                measure_country_date[m][row["code"]][row["date"]] = measure_country_date[m][row["code"]].get(
                    row["date"], getMeasure(row, m))

        for m in all_measures:
            # print(measure_country_date[m]["ITA"])
            countries_present = set()
            for date in dates:
                top_date = []
                for c in countries:
                    try:
                        top_date.append(
                            {"code": c, m: measure_country_date[m][c][date]})
                    except:
                        pass
                top_date = sorted(top_date, key=lambda x: x[m], reverse=True)
                # if date == dates[-1]:
                # print(top_date[:20])
                for t in top_date[:20]:
                    countries_present.add(t["code"])
            print(m, "ESP" in countries_present)
            # if "ITA" in countries_present:
            #     print("ITA")
            output = []
            for row in data:
                code = row["code"]
                if code in countries_present:
                    # the country will be in the top 10 at some point
                    date = row["date"]
                    try:
                        output.append({"date": date, "code": code,
                                       "value": measure_country_date[m][code][date]})
                    except Exception as e:
                        output.append({"date": date, "code": code, "value": 0})
            data = sorted(output, key=lambda x: (x["code"], x["date"]))
            country = None
            lastValue = None
            output = []
            for row in data:
                if country != row["code"]:
                    country = row["code"]
                    lastValue = row["value"]
                output.append({**row, "lastValue": lastValue})
                country = row["code"]
                lastValue = row["value"]

            if m[-1] == "a":
                multipliedOutput = []
                for row in output:
                    multipliedOutput.append(
                        {**row, "lastValue": row["lastValue"] * 1000, "value": row["value"] * 1000})
            elif m[-1] == "p":
                multipliedOutput = []
                for row in output:
                    multipliedOutput.append(
                        {**row, "lastValue": row["lastValue"] * 1000000, "value": row["value"] * 1000000})
            else:
                multipliedOutput = output
            directory = PATH+"race"
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(directory+"/"+m+".json", "w") as f:
                f.write(json.dumps({"data": multipliedOutput, "dates": dates}))


if __name__ == "__main__":
    createRace()
