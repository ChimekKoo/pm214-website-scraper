from bs4 import BeautifulSoup
import requests
import datetime

class ScrapingError(Exception):
    pass

def parse_dates_from_title(title):
    try:
        title = title.split()
        date_from, date_to = [int(x) for x in title[2].split(".")][::-1], [int(x) for x in title[4].split(".")][::-1]
        date_from, date_to = str(datetime.datetime(*date_from))[:10], str(datetime.datetime(*date_to))[:10]
        return date_from, date_to
    except ScrapingError:
        return None, None

def normalize_text(text):
    text = text.strip().replace(u'\xa0', "") 
    while "  " in text:
        text.replace("  ", " ")
    return text

def get_menu(url="https://pm214lodz.wikom.pl/strona/jadlospis", join_paragraphs=None):
    resp = requests.get(url)
    resp.raise_for_status()

    article = BeautifulSoup(resp.text, 'html.parser').find("article").find("div", class_="content-module content-module-text")
    if article is None:
        raise ScrapingError("No 'article' tags found.")
    
    title = article.find("p")
    if title is None:
        raise ScrapingError("Title not found.")
    title = title.text

    date_from, date_to = parse_dates_from_title(title)
    if date_from is None or date_to is None:
        raise ScrapingError("Problem with parsing dates from title.")

    rows = article.find("table").find("tbody").find_all("tr")[1:]
    if rows is None:
        raise ScrapingError("Problem with parsing table, 'table' or 'tbody' or 'tr' not found.")

    menu = []
    for row in rows:
        cells = row.find_all("td")
        if cells is None:
            raise ScrapingError("Problem with parsing row, 'td' in 'tr' not found.")

        date_cell = cells[0].find_all("p")
        if date_cell is None or len(date_cell) < 2:
            raise ScrapingError("Date info in row not found.")

        date = date_cell[0].text
        date = date.split("-") if "-" in date else date.split(".")
        date = [int(x) for x in date][::-1]
        date = str(datetime.datetime(*date))[:10]

        day = normalize_text(date_cell[1].text.lower())

        meals = []
        for cell in cells[1:]:
            paragraphs = []
            for p in cell.find_all("p")[:-1]:
                p_contents = []
                for el in p.children:
                    p_contents.append(normalize_text(el.text))
                paragraphs.append(" ".join(p_contents))
            if join_paragraphs is not None:
                paragraphs = join_paragraphs.join(paragraphs)
            meals.append(paragraphs)
        
        menu.append({"date": date, "day": day, "meals": meals})

    return {
        "date_from": date_from,
        "date_to": date_to,
        "menu": menu,
    }
