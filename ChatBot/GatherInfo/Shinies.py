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
    list = [cleanLine(str(line)) for line in data if str(line).startswith("<li>Shiny")
            and "Legendaries" not in str(line) and "versions" not in str(line)]

    pickle.dump(list, open("../Pickles/shiny.p", "wb"))

    # for line in data:
    #     if str(line).startswith("<li>Shiny"):
    #         printNext = False
    #         for word in re.split('[ ><]', str(line)):
    #             if printNext:
    #                 print(word)
    #                 printNext = False
    #             if word == "Shiny":
    #                 printNext = True


def cleanLine(line):
    printNext = False
    for word in re.split('[ ><]', str(line)):
        if printNext:
            return word
        if word == "Shiny":
            printNext = True


if __name__ == "__main__":
    main()