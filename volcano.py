import requests
import json
from sys import stderr
import argparse
from mastodon import Mastodon
import datetime as dt
import pytz

hashtagList = {
    "taupo":"Taupō",
    "tongariro":"Tongariro",
    "aucklandvolcanicfield":"AucklandVolcano",
    "kermadecislands":"Kermadecs",
    "mayorisland":"TūhuaMayorIsland",
    "ngauruhoe":"Ngāuruhoe",
    "northland":"NorthlandVolcano",
    "okataina":"Okataina",
    "rotorua":"Rotorua",
    "taranakiegmont":"MtTaranaki",
    "whiteisland":"Whakaari",
    "ruapehu":"Ruapehu"
}

nameSubs = {
    "whiteisland":"Whakaari/White Island",
    "mayorisland":"Tūhua/Mayor Island",
    "taupo":"Taupō"
}

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
    parser.add_argument("-u", "--unchanged", dest="unchanged", action="store_true",
                        help="post or print all even if unchanged")
    parser.add_argument("--summary", dest="summary", action="store_true",
                        help="post or print a summary, rather than changes")
    return parser.parse_args()


def getNewVolcData():
    return requests.get("https://api.geonet.org.nz/volcano/val",
                        headers={"Accept":
                                 "application/vnd.geo+json;version=2",
                                 "User-Agent": "Mastodon eqnz bot"},
                        timeout=10
                        ).text


def loadOldVolcData(fn):
    with open(fn, "r") as file:
        return file.read()


def saveVolcData(dat, fn):
    with open(fn, "w") as file:
        file.write(dat)


def VolcSummary(volcdata, minlevel = 0):
    summlist = ["{}: {} ({}) #{}".format(
        nameSubs[vol["properties"]["volcanoID"]] if
        vol["properties"]["volcanoID"] in nameSubs else vol["properties"]["volcanoTitle"],
                               vol["properties"]["level"],
                               vol["properties"]["activity"].replace(".", ""),
                               hashtagList[vol["properties"]["volcanoID"]]
                                         if vol["properties"]["volcanoID"] in
                                         hashtagList else
                                         vol["properties"]["volcanoTitle"].replace(" ", ""))
                for vol in volcdata if vol["properties"]["level"] >= minlevel]
    curTime = dt.datetime.now(tz=pytz.timezone("Pacific/Auckland")).strftime("%H:%M %A %B %-d %Y")
    if len(summlist) == 0:
        return "All volcanos at alert level 0 at " + curTime + " #VolcanoNZ"
    else:
        return "Volcano status at " + curTime + " from https://www.geonet.org.nz/volcano: #VolcanoNZ\n" + "\n".join(summlist)


def updateVolc(volfeat, oldval, args, mastodon):
    newval = volfeat["properties"]["level"]
    chword = "downgraded" if oldval >= newval else "upgraded"
    volid = volfeat["properties"]["volcanoID"]
    volc = nameSubs[volid] if volid in nameSubs else volfeat["properties"]["volcanoTitle"]
    hashtag = hashtagList[volid] if volid in hashtagList else volc.replace(" ", "")
    altext = volfeat["properties"]["activity"]
    sval = ("Volcanic alert level of {} {} from {} to {}. "
            "{}\nhttps://www.geonet.org.nz/volcano/{} "
            "#{} #VolcanoNZ").format(volc, chword, oldval,
                                 newval, altext, volid, hashtag)
    print(sval)
    if not args.debug:
        try:
            mastodon.status_post(sval)
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
        print(VolcSummary(ndj["features"], 0))
        print()
    try:
        od = loadOldVolcData(args.jfile)
        odj = json.loads(od)
    except Exception as e:
        print(e, file=stderr)
        print("File {} missing or corrupt.".format(args.jfile))
        print("Replacing with new download and quitting.")
        saveVolcData(nd, args.jfile)
        quit()
    if args.summary:
        sumstring = VolcSummary(ndj["features"], 1)
        print("Summary string:")
        print(sumstring)
        if not args.debug:
            try:
                mastodon.status_post(sumstring)
            except Exception as e:
                print(e, file=stderr)
    else:
        for vi in range(0, len(odj["features"])):
            try:
                odv = odj["features"][vi]
                ndv = ndj["features"][vi]
                if ((odv["properties"]["volcanoID"] ==
                        ndv["properties"]["volcanoID"] and
                        int(odv["properties"]["level"]) !=
                        int(ndv["properties"]["level"])) or args.unchanged):
                    updateVolc(ndv, odv["properties"]["level"], args, mastodon)
            except Exception as e:
                print(e, file=stderr)
        saveVolcData(nd, args.jfile)


if __name__ == "__main__":
    main()
