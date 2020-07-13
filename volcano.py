import requests
import json
from sys import stderr


def getNewVolcData():
    return requests.get("https://api.geonet.org.nz/volcano/val",
                        headers={"Accept":
                                 "application/vnd.geo+json;version=2",
                                 "User-Agent": "Mastodon eqnz bot"}
                        ).text


def loadOldVolcData(fn):
    with open(fn, "r") as file:
        return file.read()


def saveVolcData(dat, fn):
    with open(fn, "w") as file:
        file.write(dat)


def updateVolc(volfeat, oldval):
    newval = volfeat["properties"]["level"]
    chword = "downgraded" if oldval >= newval else "upgraded"
    volid = volfeat["properties"]["volcanoID"]
    volc = ("Whakaari/White Island" if volid == "whiteisland"
            else volfeat["properties"]["volcanoTitle"])
    altext = volfeat["properties"]["activity"]
    sval = ("Volcanic alert level of #{} {} from {} to {}. "
            "{}\nhttps://www.geonet.org.nz/volcano/{} "
            "#VolcanoNZ").format(volc, chword, oldval,
                                 newval, altext, volid)
    print(sval)


def main():
    nd = getNewVolcData()
    ndj = json.loads(nd)
    try:
        od = loadOldVolcData("volc.json")
        odj = json.loads(od)
    except Exception as e:
        print(e, file=stderr)
        saveVolcData(nd, "volc.json")
        quit()
    for vi in range(0, len(odj["features"])):
        try:
            odv = odj["features"][vi]
            ndv = ndj["features"][vi]
            if (odv["properties"]["volcanoID"] ==
                    ndv["properties"]["volcanoID"] and
                    odv["properties"]["level"] != ndv["properties"]["level"]):
                updateVolc(ndv, odv["properties"]["level"])
        except Exception as e:
            print(e, file=stderr)
    saveVolcData(nd, "volc.json")


if __name__ == "__main__":
    main()
