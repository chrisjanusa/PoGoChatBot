import pandas as pd
import pickle
from pathlib import Path


def main():
    cols = ["against_bug", 'against_dark', "against_dragon", "against_electric", "against_fairy", "against_fight",
            "against_fire", "against_flying", "against_ghost", "against_grass", "against_ground", "against_ice",
            "against_normal", "against_poison", "against_psychic", "against_rock", "against_steel", "against_water",
            "name", "pokedex_number", "type1", "type2", "generation"]

    file = Path('pokemon.csv')
    outfile = Path("../Info/pokedex.pickle")
    if not file.is_file():
        file = Path('GatherInfo/pokemon.csv')
        outfile = Path("Info/pokedex.pickle")

    df = pd.read_csv(file, skipinitialspace=True, usecols=cols)
    pokedex = {}
    for row in df.itertuples():
        temp = {}
        for i, col in enumerate(cols, start=1):
            if col.startswith("against"):
                col = col[8:]
            temp[col] = row[i]
        pokedex[row.name] = temp

    pickle.dump(pokedex, open(str(outfile), "wb"))


if __name__ == "__main__":
        main()
