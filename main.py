import re
import requests
from bs4 import BeautifulSoup
from aerodrome import Aerodrome

def get_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def get_soup(url: str, parser_type="html"):
    return BeautifulSoup(get_request(url), "{}.parser".format(parser_type))


def frame_redirect(soup: BeautifulSoup, aip_link_base: str, frame_names: list[str], traverse_links: dict):
    if len(frame_names) != 0:

        for name in frame_names:
            frame_src = aip_link_base + soup.select("frame[name={}]".format(name))[0].attrs["src"]
            frame_names.remove(name)
            traverse_links[name] = frame_src
            traverse_links = frame_redirect(get_soup(frame_src), aip_link_base, frame_names, traverse_links)
    del soup
    return traverse_links


lvnl_url = "https://www.lvnl.nl/informatie-voor-luchtvarenden/publicaties-voor-luchtvarenden"

soup = get_soup(lvnl_url)  # LVNL website
aip_link = soup.find(href=re.compile("index-en-GB.html"))["href"]
del soup
eAIP_index_soup = get_soup(aip_link)
aip_link_base = aip_link.split("index")[0]

links = dict()
frame_names = ["eAISMenuContentFrame", "eAISMenuFrameset", "eAISTabs"]
frame_redirect(eAIP_index_soup, aip_link_base, frame_names, links)
print(links)
current_aip_info = dict(get_soup(links["eAISTabs"]).select("#current-AMDT-tab")[0].attrs)
wanted_keys = ["title", "href"]

current_aip_info = {k: str(v) for k, v in current_aip_info.items() if k in wanted_keys}
current_aip_info["version"] = str(current_aip_info["href"]).replace("../", "").split("/")[0]
print(current_aip_info)


aerodromes_icao = ["EHAL", "EHAM", "EHBD", "EHBK", "EHDR", "EHEH", "EHGG", "EHHO", "EHHV", "EHKD",
                   "EHLE", "EHMZ", "EHOW", "EHRD", "EHSE", "EHST", "EHTE", "EHTL", "EHTW", "EHTX"]
aerodromes_icao = ["EHAL", "EHBD", "EHDR", "EHEH", "EHHO", "EHHV", "EHMZ", "EHOW", "EHSE", "EHST", "EHTE", "EHTL",
                   "EHTX", "EHLE", "EHKD"]

print(aip_link_base)
current_AD_html_link_base = re.sub('[0-9]{4}-[0-9]{2}-[0-9]{2}-[A-Z]{5}', current_aip_info["version"], aip_link_base)
current_AD_html_link = current_AD_html_link_base + "/eAIP/EH-AD-2.{}-en-GB.html#AD-2"



def html_distance_table_to_json(soup: BeautifulSoup, icao_name: str):

    if soup is not None:
        runway_data_dict = dict()
        for tag in soup.find("tbody").findAll("td"):
            try:
                tag.find("del").clear()
            except AttributeError:
                pass
        raw_distances = (x for x in (tbody.findAll("td") for tbody in soup.find("tbody")) if x)

        multiple_distances_runway = []
        for runway in raw_distances:

            if len(runway) == 6:
                runway_designator = runway[0].text
                tora = runway[1].text
                toda = runway[2].text
                asda = runway[3].text
                lda = runway[4].text
                remarks = runway[5].text
                runway_data_dict[runway_designator] = {"TORA": tora, "TODA": toda, "ASDA": asda,
                                                       "LDA": lda, "Remarks": remarks}
                current_runway = runway_designator

            elif len(runway) != 6:

                if len(runway[0].text) > 2:
                    tora = runway[0].text
                    toda = runway[1].text
                    asda = runway[2].text
                    lda = runway[3].text
                    remarks = runway[4].text

                    multiple_distances_runway.append({"TORA": tora, "TODA": toda, "ASDA": asda,
                                                      "LDA": lda, "Remarks": remarks})
                    runway_data_dict[current_runway] = multiple_distances_runway
                else:

                    for i in range(len(runway)):
                        try:
                            runway[i] = runway[i].text.split(" ")[0]
                        except:
                            pass

                    if len(runway[-1]) < 5:
                        runway_designator = runway[0]
                        tora = runway[1]
                        toda = runway[2]
                        asda = runway[3]
                        lda = runway[4]
                        multiple_distances_runway.append({"TORA": tora, "TODA": toda, "ASDA": asda,
                                                          "LDA": lda, "Remarks": remarks})
                        runway_data_dict[runway_designator] = multiple_distances_runway

        return runway_data_dict
    else:
        return {None, None}


aerodrome_information = dict()
aerodrome_objects = dict()
for aerodrome in aerodromes_icao:
    current_aerodrome_info = dict()

    soup = get_soup(current_AD_html_link.format(aerodrome))
    aerodrome_objects[aerodrome] = Aerodrome(aerodrome)
    runway_characteristics = soup.find(id="{}-ad-2.12".format(aerodrome.lower()))
    declared_distances = soup.find(id="{}-ad-2.13".format(aerodrome.lower()))

    distances = html_distance_table_to_json(declared_distances, aerodrome)
    aerodrome_objects[aerodrome].set_runway_distances(distances)
    aerodrome_information[aerodrome] = aerodrome_objects[aerodrome].get_runway_distances()



print(aerodrome_information)
