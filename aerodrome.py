"""
Format of declared distances:  {"RWY": {"08": {"TORA": None, "TODA": None, "ASDA": None,
                                     "LDA": None, "Remarks": None},
                              "26": {"TORA": None, "TODA": None, "ASDA": None,
                                     "LDA": None, "Remarks": None}}}

"""


class Aerodrome:
    def __init__(self, icao_code: str):
        super().__init__()
        self.icao_code = icao_code.upper()
        self.runway_information = {"RWY": {}}

    def set_runway_distances(self, declared_distances: dict):
        self.runway_information["RWY"] = declared_distances

    def get_runway_distances(self) -> dict:
        return self.runway_information

    def __str__(self):
        return "Aerodrome information for {}.".format(self.icao_code)
