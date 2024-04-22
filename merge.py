from shapely.geometry import LinearRing, Polygon
from shapely.ops import unary_union

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
    print(f"processing {len(data)} files")
    for alt in alts:
        print(f"processing rings for {alt}")
        polygons = []
        for i in range(0, len(data)):
            polygons.append(
                Polygon(
                    shell=LinearRing(
                        [r["points"] for r in data[i]["rings"] if r["alt"] == alt][0]
                    )
                )
            )
        to_consider = [0]
        for i in range(1, len(data)):
            combined = False
            for j in to_consider:
                if polygons[j].disjoint(polygons[i]):
                    print(f"{alt}: polgon {i} disjoint {j}")
                else:
                    print(f"{alt} combine polygons {i} and {j}")
                    p = unary_union([polygons[j], polygons[i]])
                    polygons[j] = p
                    combined = True
            if not combined:
                to_consider.append(i)
        for i in to_consider:
            points = [[x, y] for x, y in polygons[i].exterior.coords]
            result["rings"].append({"points": points, "alt": alt})

    with open("combined.json", "w") as out:
        print(json.dumps(result), file=out)
