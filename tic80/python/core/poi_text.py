def poi_type_label(poi_type: str) -> str:
    if poi_type == "gas_station":
        return "gas station"
    if poi_type == "scrapyard":
        return "scrapyard"
    if poi_type == "depot":
        return "depot"
    return str(poi_type).replace("_", " ")
