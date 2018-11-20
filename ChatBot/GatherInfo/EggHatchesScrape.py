from bs4 import BeautifulSoup
import requests


def main():

    #scrape the website for raw text data
    u = "https://www.eurogamer.net/articles/2018-11-18-pokemon-go-eggs-chart-hatching-2km-5km-7km-10km-eggs"
    webpage = requests.get(u).text
    soup = BeautifulSoup(webpage, features="html.parser")
    data = str(soup.findAll()).split("\n")

    #initialize lists of egg hatches as empty lists
    eggs_2k = []
    eggs_5k = []
    eggs_7k = []
    eggs_10k = []

    #keep track of which list we are in (2k, 5k, 7k, or 10k, or 0 if not in a list)
    cur_egg = 0

    #go through each line of scraped text
    for line in data:
        #set cur_egg to the corresponding list one we find the header that states it
        if line.startswith("<h2 id=\"section-1"): #2k egg
            cur_egg = 2
        elif line.startswith("<h2 id=\"section-2"): #5k egg
            cur_egg = 5
        elif line.startswith("<h2 id=\"section-3"): #7k egg
            cur_egg = 7
        elif line.startswith("<h2 id=\"section-4"): #10k egg
            cur_egg = 10
        elif line.startswith("<h2 id=\"section-5"): #not a list of egg hatches
            cur_egg = 0

        #if a pokemon name is found, add it to list corresponding to the cur_egg
        #Alolan pokemon have hyperlinks in name, ignore that hyperlink and extract rest of text name
        elif line.startswith("<li><a href=\"https://www.eurogamer.net/articles/2018-08-01-pokemon-go-alolan-forms-5392\">Alolan</a>"):
            start = len("<li><a href=\"https://www.eurogamer.net/articles/2018-08-01-pokemon-go-alolan-forms-5392\">Alolan</a> ")
            end = line.find("<", start)
            pokemon = "Alolan "
            pokemon += line[start:end]
            eggs_7k.append(pokemon)
        elif line.startswith("<li>"):
            start = len("<li>")
            end = line.find(" (", start)
            pokemon = line[start:end]
            if cur_egg == 2:
                eggs_2k.append(pokemon)
            elif cur_egg == 5:
                eggs_5k.append(pokemon)
            elif cur_egg == 7:
                eggs_7k.append(pokemon)
            elif cur_egg == 10:
                eggs_10k.append(pokemon)

    #save lists into data file
    with open("../Info/EggHatches.py", "w") as pokemon_file:
        pokemon_file.write("HATCHES_2K = {\n")
        first = True
        for pokemon in set(eggs_2k):
            if first:
                pokemon_file.write("    \"" + pokemon + "\"")
                first = False
            else:
                pokemon_file.write(",\n    \"" + pokemon + "\"")
        pokemon_file.write("}\n")

        pokemon_file.write("\nHATCHES_5K = {\n")
        first = True
        for pokemon in set(eggs_5k):
            if first:
                pokemon_file.write("    \"" + pokemon + "\"")
                first = False
            else:
                pokemon_file.write(",\n    \"" + pokemon + "\"")
        pokemon_file.write("}\n")

        pokemon_file.write("\nHATCHES_7K = {\n")
        first = True
        for pokemon in set(eggs_7k):
            if first:
                pokemon_file.write("    \"" + pokemon + "\"")
                first = False
            else:
                pokemon_file.write(",\n    \"" + pokemon + "\"")
        pokemon_file.write("}\n")

        pokemon_file.write("\nHATCHES_10K = {\n")
        first = True
        for pokemon in set(eggs_10k):
            if first:
                pokemon_file.write("    \"" + pokemon + "\"")
                first = False
            else:
                pokemon_file.write(",\n    \"" + pokemon + "\"")
        pokemon_file.write("}\n")


if __name__ == "__main__":
    main()
