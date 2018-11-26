import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path


def main():
    u = "https://serebii.net/pokemongo/pokemon.shtml"

    webpage = requests.get(u).text
    soup = BeautifulSoup(webpage, features="html.parser")
    data = str(soup.findAll()).split("\n")
    pokemon_avail = []
    pokemon_not_avail = []
    has_alola = []
    regionals = []
    for line in data:
        if line.startswith("<a href=\"/pokemongo/pokemon/") and ">- In-Depth" not in line:
            start = len("<a href=\"/pokemongo/pokemon/031.shtml\">")
            end = line.find("</a>", start)
            if line.find(u"\u2642") != -1:
                end = line.find(u"\u2642")
            if line.find(u"\u2640") != -1:
                end = line.find(u"\u2640")
            pokemon = line[start:end]
            if "<i>Not currently available</i>" in line:
                pokemon_not_avail.append(pokemon)
            else:
                if "Alola" in line:
                    has_alola.append(pokemon)
                if "Only available in" in line:
                    regionals.append(pokemon)
                pokemon_avail.append(pokemon)
    shiny = get_shiny_list()

    outfile = Path("../Info/Pokemon.py")
    if not outfile.is_file():
        outfile = Path("Info/Pokemon.py")

    with open(str(outfile), "w") as pokemon_file:
        pokemon_file.write("POKEMON_AVAIL = {\n")
        first = True
        for pokemon in set(pokemon_avail):
            if first:
                pokemon_file.write("    \"" + pokemon + "\"")
                first = False
            else:
                pokemon_file.write(",\n    \"" + pokemon + "\"")
        pokemon_file.write("}\n")

        pokemon_file.write("\nPOKEMON_NOT_AVAIL = {\n")
        first = True
        for pokemon in set(pokemon_not_avail):
            if first:
                pokemon_file.write("    \"" + pokemon + "\"")
                first = False
            else:
                pokemon_file.write(",\n    \"" + pokemon + "\"")
        pokemon_file.write("}\n")

        pokemon_file.write("\nALOLA_POKEMON = {\n")
        first = True
        for pokemon in set(has_alola):
            if first:
                pokemon_file.write("    \"" + pokemon + "\"")
                first = False
            else:
                pokemon_file.write(",\n    \"" + pokemon + "\"")
        pokemon_file.write("}\n")

        pokemon_file.write("\nREGIONAL_POKEMON = {\n")
        first = True
        for pokemon in set(regionals):
            if first:
                pokemon_file.write("    \"" + pokemon + "\"")
                first = False
            else:
                pokemon_file.write(",\n    \"" + pokemon + "\"")
        pokemon_file.write("}\n")

        pokemon_file.write("\nSHINY_POKEMON = {\n")
        first = True
        for pokemon in set(shiny):
            if first:
                pokemon_file.write("    \"" + pokemon + "\"")
                first = False
            else:
                pokemon_file.write(",\n    \"" + pokemon + "\"")
        pokemon_file.write("}\n")


def get_shiny_list():
    u = "https://www.imore.com/pokemon-go-shiny"

    webpage = requests.get(u).text
    soup = BeautifulSoup(webpage, features="html.parser")
    data = soup.findAll()
    shiny_list = [clean_line(str(line)) for line in data if str(line).startswith("<li>Shiny")
                  and "Legendaries" not in str(line) and "versions" not in str(line)]
    return shiny_list


def clean_line(line):
    print_next = False
    for word in re.split('[ ><]', str(line)):
        if print_next:
            return word
        if word == "Shiny":
            print_next = True


if __name__ == "__main__":
    main()
