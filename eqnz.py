import time
import signal
import requests
import dateutil.parser
import datetime
import argparse
from sys import stderr
from pytz import timezone

roman = {1: "I (Unnoticeable)",
         2: "II (Unnoticeable)",
         3: "III (Weak)",
         4: "IV (Light)",
         5: "V (Moderate)",
         6: "VI (Strong)",
         7: "VII (Severe)",
         8: "VIII (Extreme)",
         9: "IX (Extreme)",
         10: "X (Extreme)",
         11: "XI (Extreme)",
         12: "XII (Extreme)"}

def parseArgs():
    parser = argparse.ArgumentParser(description="EQNZ mastodon bot")
    parser.add_argument("-m", "--mmi", type=int, default=-1, dest="mmi",
                        help="minimum Modified Mercalli Intensity (MMI).",
                        choices=range(-1,8), metavar = "[-1 to 8]")
    parser.add_argument("-s", "--secret", type=str, metavar = "[file]",
                        default="eqnz_usercred.secret",
                        help="mastodon secret file", dest="secret")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true",
                        help="do not post to mastodon")
    return parser.parse_args()

def latestQuakes(mmi):
    try:
        resp = requests.get("https://api.geonet.org.nz/quake",
            headers = {"Accept": "application/vnd.geo+json;version=2"},
            params = {"MMI": mmi})

        eqjs = resp.json()["features"]
        eqs = {}
        for eq in eqjs:
            thiseq = {
                "coordinates": eq["geometry"]["coordinates"],
                "time": dateutil.parser.isoparse(eq["properties"]["time"]).
                            astimezone(tz=timezone("Pacific/Auckland")),
                "depth": round(float(eq["properties"]["depth"]), 1),
                "magnitude": round(float(eq["properties"]["magnitude"]), 1),
                "mmi": eq["properties"]["mmi"],
                "locality": eq["properties"]["locality"],
                "quality": eq["properties"]["quality"]
            }
            eqs[eq["properties"]["publicID"]] = thiseq
        return eqs
    except Exception as e:
        print(e, file=stderr)
        return {}

def printEQ(eq, eqid, threadid, args):
    global roman
    if threadid is not None:
        ps1 = "Update on earthquake "
    else:
        ps1 = "Earthquake "
    ps2 = ("at {time:%-I:%M %p}, {locality}.\nMagnitude {magnitude:.1f}, at "
          "a depth of {depth:.1f} kilometres.").format(**eq)
    if eq["mmi"] in roman:
        ps3 = "\nModified Mercalli Intensity: {}".format(roman[eq["mmi"]])
    else:
        ps3 = ""
    if (eq["quality"] != "best" or threadid is not None):
        ps4 = "\nData quality: {}". format(eq["quality"])
    else:
        ps4 = ""
    if threadid is None:
        ps5 = "\nhttps://www.geonet.org.nz/earthquake/{}".format(eqid)
    else:
        ps5 = ""
    post = "{}{}{}{}{}".format(ps1, ps2, ps3, ps4, ps5)
    print(post)
    if args.debug:
        print("noMasto")
    else:
        print("Masto")

    # Placeholder id
    return "123456789"

def main():
    args = parseArgs()
    eqs = latestQuakes(args.mmi)

    if len(eqs) == 0:
        raise ValueError("Failed to get first batch of earthquakes")

    while True:
        print("looping...")
        time.sleep(60)
        neweq = latestQuakes(args.mmi)
        for qid in neweq:
            if neweq[qid]["quality"] == "deleted":
                continue
            if qid in eqs:
                if (eqs[qid]["magnitude"] != neweq[qid]["magnitude"] or
                        eqs[qid]["time"] != neweq[qid]["time"] or
                        eqs[qid]["depth"] != neweq[qid]["depth"] or
                        eqs[qid]["locality"] != neweq[qid]["locality"]):
                    # Modified entry
                    tid = (eqs[qid]["threadid"] if
                        "threadid" in eqs[qid] else None)
                    neweq[qid]["threadid"] = printEQ(neweq[qid], qid, tid, args)
                    eqs[qid] = neweq[qid]
            else:
                # New entry
                neweq[qid]["threadid"] = printEQ(neweq[qid], qid, None, args)
                eqs[qid] = neweq[qid]

if __name__ == "__main__":
    main()
