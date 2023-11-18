from shapely.geometry import (
    LinearRing,
    Polygon,
)
import json
import pathlib
import sys


def handle_command_line_arguments():
    _json_files = []
    for i in range(1, len(sys.argv)):
        if pathlib.Path(sys.argv[i]).exists():
            _json_files.append(sys.argv[i])
    return _json_files


if __name__ == "__main__":
    json_files = handle_command_line_arguments()
    data = []
    for f in json_files:
        with open(f, "r") as jf:
            data.append(json.load(jf))

    alts = [r["alt"] for r in data[0]["rings"]]
    result = {
        "id": "CALCDND",
        "lon": data[0]["lon"],
        "lat": data[0]["lat"],
        "refraction": "0.25",
        "elev_amsl": data[0]["elev_amsl"],
        "rings": [],
    }

    polygon = []
    for alt in alts:
        polygon[alt] = []
        for i in range(0, len(data)):
            polygon[alt][i] = Polygon(
                shell=LinearRing(
                    [r["points"] for r in data[i]["rings"] if r["alt"] == alt][0]
                )
            )
        for i in range(1, len(data)):
            polygon[alt][0].union(polygon[alt][i])
        points = [[x, y] for x, y in polygon[0].exterior.coords]
        result["rings"].append([{"points": points, "alt": alt}])

    with open("combined.json", "w") as out:
        print(json.dumps(result), file=out)
