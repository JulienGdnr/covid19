# -*- coding: utf-8 -*-
from os.path import isfile, join
from os import listdir
import json
from datetime import datetime
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

onlyfiles = [f for f in listdir(PATH+"race") if isfile(join(PATH+"race", f))]


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


start_dates = {}
with open(PATH+"race/deaths.json") as f:
    data = json.loads(f.read())
    dates = data["dates"]
    data = data["data"]
    for el in data:
        if el["value"] >= 10 and el["lastValue"] <= 10:
            start_dates[el["code"]] = int(el["date"].replace("-", ""))
            if el["code"] == "USA":
                print(el["code"], el["value"], el["lastValue"])

print(start_dates)
for fle in onlyfiles:
    output = []
    with open(PATH+"race/"+fle) as f:
        data = json.loads(f.read())
    data = data["data"]
    code = None
    count = 0
    m = 0
    # print(len(data))
    for i, row in enumerate(data):
        if row["code"] != code:
            code = row["code"]
            count = 0
        d = int(row["date"].replace("-", ""))
        try:
            if d >= start_dates[code]:
                row["i"] = count
                output.append(row)
                m = max(m, count)
                count += 1
        except:
            pass
    directory = PATH+"line"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(directory+"/"+fle, "w") as f:
        f.write(json.dumps({"data": output, "range": m}))
# print(start_dates)
