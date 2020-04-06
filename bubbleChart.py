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


def createBubble(continent=False):
    o = {}
    r = 0
    for m in all_measures:
        p = PATH+"line/"+m+".json" if not continent else PATH+"line-continent/"+m+".json"
        with open(p, "r") as f:
            data = json.loads(f.read())
            for row in data["data"]:
                o[row["date"]] = o.get(row["date"], {})
                o[row["date"]][row["code"]] = o[row["date"]].get(
                    row["code"], {})
                o[row["date"]][row["code"]][m] = row["value"]
                o[row["date"]][row["code"]]["i"] = row["i"]
            r = data["range"]

    output = []
    for date, value in o.items():
        for code, value2 in value.items():
            output.append({**value2, "code": code, "date": date})
    output = sorted(output, key=lambda x: (x["code"], x["date"]))
    with open(PATH+f"bubble{'-continent' if continent else ''}.json", "w") as f:
        f.write(json.dumps({"data": output, "range": r}))


if __name__ == "__main__":
    createBubble()
