
import unicodedata
from xml.etree import ElementTree
import httpx
import time
import json
from loguru import logger


def parse_chapter(chap_str):
    """Parse the chapter number.
    """
    if "incip" in chap_str.lower():
        return "Incipit"
    return chap_str.split("K")[1]


def parse_verse(verse_str):
    """Parse the verse number.
    """
    return verse_str.split("V")[1]


def parse_manuscript(response_str, book_id="B20"):
    et = ElementTree.fromstring(response_str.replace('<lb break="no"/>', "").replace('<lb/>', ''))
    title = et.find(".//{http://www.tei-c.org/ns/1.0}title").attrib["n"]
    flat_text = {}

    USE_RECONSTRUCTED = True

    for elem in et.iter():
        if elem.tag == "{http://www.tei-c.org/ns/1.0}div":
            if elem.attrib["type"] == "book":
                book = elem.attrib["n"]
                if book != book_id:
                    break
            if elem.attrib["type"] == "chapter":
                chapter = parse_chapter(elem.attrib["n"])
                if chapter not in flat_text:
                    flat_text[chapter] = {}
            if elem.attrib["type"] == "incipit":
                chapter = parse_chapter(elem.attrib["n"])
                if chapter not in flat_text:
                    flat_text[chapter] = {}

        if elem.tag == "{http://www.tei-c.org/ns/1.0}ab":
            if elem.attrib.get("n"):
                verse = parse_verse(elem.attrib["n"])
            try:
                verse
            except UnboundLocalError:
                verse = "0"
            if verse not in flat_text[chapter]:
                flat_text[chapter][verse] = ""
        if elem.tag == "{http://www.tei-c.org/ns/1.0}w":
            if USE_RECONSTRUCTED:
                for subelem in elem.iter():
                    if subelem.text:
                        flat_text[chapter][verse] += subelem.text
                flat_text[chapter][verse] += " "
            else:
                if elem.text:
                    flat_text[chapter][verse] += elem.text + " "
                elif not USE_RECONSTRUCTED and not elem.text:
                    flat_text[chapter][verse] += "-"
                else:
                    flat_text[chapter][verse] += " "
    return title, flat_text


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


if __name__ == "__main__":
    # oncials = [f"2{str(i).zfill(4)}" for i in range(1, 300, 1)]
    # papyrus = [f"1{str(i).zfill(4)}" for i in range(1, 250, 1)]
    miniscules = [f"3{str(i).zfill(4)}" for i in range(362, 3000, 1)]

    manuscripts = ['20001',
                   '20002',
                   '20003',
                   '20004',
                   '20005',
                   '20019',
                   '20032',
                   '20036',
                   '20037',
                   '20038',
                   '20250',
                   '10003',
                   '10004',
                   '10042',
                   '10045',
                   '10075',
                   '30001',
                   '30013',
                   '30018',
                   '30022',
                   '30033',
                   '30069',
                   '30079',
                   '30343',
                   '30362',
                   '32737']
    # MANUSCRIPT_LIST = oncials + papyrus + miniscules
    MANUSCRIPT_LIST = manuscripts #+ miniscules
    base_url = "https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"

    tradition_name = "Luke1,Luke10,Luke20"
    ix = 0
    responses = []
    for manuscript in MANUSCRIPT_LIST:
        logger.info(f"Trying retrieval of {manuscript}")
        request = f"?docID={manuscript}&indexContent={tradition_name}&fullPage=true&format=xml"
        response = httpx.get(base_url + request, timeout=60)
        if response.status_code == 200:
            if "No Transcription Available" in response.text:
                pass
            else:
                responses.append(remove_control_characters(response.text))
                logger.info(f"Downloaded manuscript {manuscript}")
                ix += 1
            time.sleep(30)  # Avoid reset by peer errors
    logger.info(f"Retrieved {ix} manuscript")

    parsed_manuscripts = {}
    for ix, manuscript in enumerate(responses):
        try:
            title, parsed = parse_manuscript(manuscript, book_id="B03")
            parsed_manuscripts[title] = parsed
        except ElementTree.ParseError:
            print(ix)
            continue
        except UnboundLocalError:
            print(ix)
            continue

    with open("data/ms_372.xml", "r") as f:
        ms_372 = parse_manuscript(f.read(), "B03")

    parsed_manuscripts["372"] = ms_372[1]

    with open("data/manuscripts.json", "w", encoding="utf-8") as f:
        json.dump(parsed_manuscripts, f, ensure_ascii=False)
