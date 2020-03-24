# -*- coding: utf-8 -*-
import json
import os

all_measures = ["deaths", "recovered",
                "confirmed", "confirmed_deaths_recovered"]

PATH = "./covid19/public/"

measure_country_date = {}
dates = []


def getMeasure(row, m):
    if "_" in m:
        arr = m.split("_")
        return [int(row.get(arr[0], 0)), int(row.get(arr[1], 0)), int(row.get(arr[2], 0))]
    else:
        return [int(row.get(m, 0)), 0, 0]


def getDivisionMeasure(o, m):
    if "_" not in m:
        return int(o.get("m1", 0))
    return o["m1"] - o["m2"] - o["m3"]


def createArray(code, measure):
    output = []
    for d in dates:
        try:
            val = measure_country_date[measure][code][d]
        except:
            val = 0
        output.append(val)
    return output


with open(PATH + "data.json") as f:
    data = json.loads(f.read())
    # for i in range(1, 30):
    dates = set([_["date"] for _ in data])
    dates = sorted(dates)
    o = {}

    for row in data:
        for m in all_measures:
            measure_country_date[m] = measure_country_date.get(m, {})
            measure_country_date[m][row["code"]
                                    ] = measure_country_date[m].get(row["code"], {})
            if m not in row.keys() or not row[m]:
                measure_country_date[m][row["code"]][row["date"]] = 0
            else:
                measure_country_date[m][row["code"]][row["date"]] = measure_country_date[m][row["code"]].get(
                    row["date"], float(row.get(m, 0)))

    for m in all_measures:
        o[m] = o.get(m, {})
        for row in data:
            if row["date"] == dates[-1]:
                o[m][row["code"]] = o[m].get(
                    row["code"], {"m1": 0, "m2": 0, 'm3': 0})
                m1, m2, m3 = getMeasure(row, m)
                o[m][row["code"]]["m1"] += m1
                o[m][row["code"]]["m2"] += m2
                o[m][row["code"]]["m3"] += m3
        arr = [{"code": k, "m": getDivisionMeasure(
            v, m)} for k, v in o[m].items()]
        arr = sorted(arr, key=lambda x: x["m"], reverse=True)
        countries = []
        for k in range(1, 30):
            output = []
            others = []
            others_1 = []
            others_2 = []
            for j, row in enumerate(arr):
                if j < k:
                    if '_' in m:
                        m1 = m.split("_")[0]
                        m2 = m.split("_")[1]
                        m3 = m.split("_")[2]
                        a_1 = createArray(row["code"], m1)
                        a_2 = createArray(row["code"], m2)
                        a_3 = createArray(row["code"], m3)
                        output.append({"code": row["code"], "measure": m, "values": [
                                      a_1[i]-a_2[i]-a_3[i] for i in range(len(a_1))]})
                    else:
                        values = createArray(row["code"], m)
                        output.append(
                            {"code": row["code"], "measure": m, "values": values})
                else:  # others
                    if "_" in m:
                        m1 = m.split("_")[0]
                        m2 = m.split("_")[1]
                        m3 = m.split("_")[2]
                        a_1 = createArray(row["code"], m1)
                        a_2 = createArray(row["code"], m2)
                        a_3 = createArray(row["code"], m3)
                        others.append({"code": row["code"], "measure": m, "values": [
                                      a_1[i]-a_2[i]-a_3[i] for i in range(len(a_1))]})
                    else:
                        values = createArray(row["code"], m)
                        others.append(values)
            temp = []
            if "_" in m:
                for i, date in enumerate(dates):
                    res_1 = 0
                    for j in range(len(others)):
                        # print(len(others), others[0], j, i)
                        res_1 += others[j]["values"][i]
                    temp.append(res_1)
            else:
                for i, date in enumerate(dates):
                    res = 0
                    for j in range(len(others)):
                        # print(others, j, i)
                        res += others[j][i]
                    temp.append(res)
            output.append({"code": "others", "measure": m, "values": temp})
            directory = PATH+"vertical"
            if not os.path.exists(directory):
                os.makedirs(directory)
            directory += "/" + m
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(directory+"/"+str(k)+".json", "w") as f:
                f.write(json.dumps({"data": output, "dates": dates}))
