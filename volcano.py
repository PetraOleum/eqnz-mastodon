import requests
import json
from sys import stderr
import argparse
from mastodon import Mastodon

def parseArgs():
    parser = argparse.ArgumentParser(description=("EQNZ mastodon bot: volcano "
                                                  "alert levels"))
    parser.add_argument("-j", "--json", type=str, metavar="FILE",
                        default="volc.json",
                        help=("json file, default: "
                              "volc.json"), dest="jfile")
    parser.add_argument("-s", "--secret", type=str, metavar="FILE",
                        default="eqnz_usercred.secret",
                        help=("mastodon secret file, default: "
                              "eqnz_usercred.secret"), dest="secret")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true",
                        help="do not post to mastodon, do print initial")
    return parser.parse_args()


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


def updateVolc(volfeat, oldval, args, mastodon):
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
    if not args.debug:
        try:
            masto.status_post(sval)
        except Exception as e:
            print(e, file=stderr)



def main():
    args = parseArgs()
    if not args.debug:
        mastodon = Mastodon(access_token=args.secret)
    else:
        mastodon = None
    nd = getNewVolcData()
    ndj = json.loads(nd)
    if args.debug:
        for vol in ndj["features"]:
            print("{}: {} ({})".format(vol["properties"]["volcanoTitle"],
                                       vol["properties"]["level"],
                                       vol["properties"]["activity"]))
    try:
        od = loadOldVolcData(args.jfile)
        odj = json.loads(od)
    except Exception as e:
        print(e, file=stderr)
        saveVolcData(nd, args.jfile)
        quit()
    for vi in range(0, len(odj["features"])):
        try:
            odv = odj["features"][vi]
            ndv = ndj["features"][vi]
            if (odv["properties"]["volcanoID"] ==
                    ndv["properties"]["volcanoID"] and
                    int(odv["properties"]["level"]) !=
                    int(ndv["properties"]["level"])):
                updateVolc(ndv, odv["properties"]["level"])
        except Exception as e:
            print(e, file=stderr)
    saveVolcData(nd, args.jfile)


if __name__ == "__main__":
    main()
