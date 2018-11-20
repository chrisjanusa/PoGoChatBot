from Info.pokemon import SHINY_POKEMON


class Trainer(object):
    name = ""
    age = 0
    team = ""
    level = -1
    favorite_pokemon = ""
    caught_pokemon = []

    def favorite_shiny(self):
        return self.favorite_pokemon in SHINY_POKEMON
