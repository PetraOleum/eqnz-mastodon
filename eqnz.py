import requests

resp = requests.get("https://api.geonet.org.nz/quake",
    headers = {"Accept": "application/vnd.geo+json;version=2"},
    params = {"MMI": "-1"})

eqjs = resp.json()["features"]
eqs = {}
for eq in eqjs:
    thiseq = {
        "coordinates": eq["geometry"]["coordinates"],
        "time": eq["properties"]["time"],
        "depth": eq["properties"]["depth"],
        "magnitude": eq["properties"]["magnitude"],
        "mmi": eq["properties"]["mmi"],
        "locality": eq["properties"]["locality"],
        "quality": eq["properties"]["quality"]
    }
    eqs[eq["properties"]["publicID"]] = thiseq

for eq in eqs:
    print(eq)
    print(eqs[eq])

print("2020p516546" in eqs)
print("2030p516546" in eqs)

eqs.pop("2020p516546", None)
print("2020p516546" in eqs)
