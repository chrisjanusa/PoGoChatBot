import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pickle


def main():
    u = "https://www.imore.com/pokemon-go-shiny"

    req = Request(
        u,
        headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, features="html.parser")
    data = soup.findAll()
    list = [clean_line(str(line)) for line in data if str(line).startswith("<li>Shiny")
            and "Legendaries" not in str(line) and "versions" not in str(line)]

    with open("../shiny.py", "w") as shinies:
        shinies.write("SHINY_POKEMON = {\n")
        first = True
        for shiny in list:
            if first:
                shinies.write("    \"" + str(shiny) + "\"")
                first = False
            else:
                shinies.write(",\n    \"" + str(shiny) + "\"")
        shinies.write("}\n")


def clean_line(line):
    print_next = False
    for word in re.split('[ ><]', str(line)):
        if print_next:
            return word
        if word == "Shiny":
            print_next = True


if __name__ == "__main__":
    main()
