# Chris Janusa and Nymisha Jahagirdar
# Inspired by BroBot available at https://github.com/lizadaly/brobot/
import os
from textblob import TextBlob
from pathlib import Path

from Find import *
from Info.GenericResponses import *
from Info.Facts import *
from Info.Pokemon import *

from Trainer import Trainer

nlp = spacy.load('en_core_web_sm')
os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'
logging.basicConfig(filename='log_file.log')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main():
    user_statement = proccess_sentance(input(random.choice(INRODUCTION) + "\n> "))

    while user_statement.name == "":
        blob = TextBlob(user_statement.text)
        if blob.sentiment.polarity < 0.1:
            user_statement = proccess_sentance(input(random.choice(NO_NAME_SASSY) + "\n> "))
        else:
            user_statement = proccess_sentance(input(random.choice(NO_NAME) + "\n> "))

    name = user_statement.name

    pickle_path = Path("dict.pickle")
    if pickle_path.is_file():
        with open(str(pickle_path), "rb") as pickle_file:
            trainers = pickle.load(pickle_file)
    else:
        trainers = {}

    if name in trainers:
        trainer = trainers[name]
        if trainer.team != "":
            user_statement = proccess_sentance(input(
                random.choice(RETURN_TRAINER).format(**{'name': name}) + " btw Go " + trainer.team + "!!!!!!" + "\n> "))
        else:
            user_statement = proccess_sentance(input(random.choice(RETURN_TRAINER).format(**{'name': name}) + "\n> "))

    else:
        trainer = Trainer(name)
        trainers[name] = trainer
        user_statement = proccess_sentance(input(random.choice(NEW_TRAINER).format(**{'name': name}) + "\n> "))

    rep_type = ""
    while not user_statement.isFarewell:
        reply, rep_type = get_reply(user_statement, trainer, rep_type)
        user_statement = proccess_sentance(input(reply + "\n>"))

    print(random.choice(BYE))
    with open(str(pickle_path), "wb") as pickle_file:
        pickle.dump(trainers, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)


def hatches_from(num, pokemon):
    if num == 2:
        hatches = HATCHES_2K
    if num == 5:
        hatches = HATCHES_5K
    if num == 7:
        hatches = HATCHES_7K
    if num == 10:
        hatches = HATCHES_10K

    if pokemon in hatches:
        samp = random.sample(hatches, 5)
        samp.append("your favorite pokemon " + pokemon)
        return samp
    return random.sample(hatches, 6)


def get_num_pokemon(num):
    with open("./Info/pokedex.pickle", "rb") as pokedex_file:
        pokedex = pickle.load(pokedex_file)
        for key, value in pokedex.items():
            if value["pokedex_number"] == num:
                return value["name"]
    return ""


def get_reply(parse_obj, curr_trainer, rep_type):
    pronoun = parse_obj.pronoun
    subj = parse_obj.subj
    adj = parse_obj.adj
    doj = parse_obj.doj
    verb = parse_obj.verb
    name = parse_obj.name
    num = parse_obj.num
    is_egg = parse_obj.isEgg
    pokemon = parse_obj.pokemon
    imp_terms = parse_obj.imp_terms
    team = parse_obj.team


    # Maintains topic so if no pokemon are present assume it is referring to previous topic
    if not pokemon and rep_type in ALL_POKEMON:
        pokemon.append(rep_type)

    # Pattern "Does {pokemon} have an Alolan form?"
    if ("be" in verb  or "have" in verb) and pokemon and "Alolan" in imp_terms:
        if pokemon[0] in ALOLA_POKEMON:
            return pokemon[0] + " does have an Alolan form", pokemon[0]
        else:
            return "Nope, " + pokemon[0] + " doesn't have an Alolan form", pokemon[0]

    if ("be" in verb  or "have" in verb) and pokemon and "Regional" in imp_terms:
        if pokemon[0] in REGIONAL_POKEMON:
            return pokemon[0] + " is a regional pokemon", pokemon[0]
        else:
            return "Nope, " + pokemon[0] + " is available all over the world", pokemon[0]

    # Pattern "What pokemon is {num}?
    if ("be" in verb  or "have" in verb) and num != -1:
        pokemon = get_num_pokemon(num)
        if pokemon != "":
            return "#" + str(num) + " is " + pokemon, pokemon

    # Pattern "Can {pokemon} be shiny?"
    if pokemon and "Shiny" in imp_terms and ("be" in verb  or "have" in verb):
        return get_shiny_reply(pokemon[0])

    # Pattern "What hatches from {num} egg?"
    if is_egg and not pokemon:
        hatch_list = hatches_from(num, curr_trainer.fav)
        last = hatch_list.pop()
        return "To name a few: " + ", ".join(hatch_list) + " and " + last + " hatch from " + str(num) + "km eggs", str(
            num) + "km"

    # Pattern "What is {imp_term}?" and "What type is {pokemon}?
    if imp_terms and "be" in verb:
        if "Type" in imp_terms and pokemon:
            return pokemon[0] + " is a " + find_type(pokemon[0]) + " type pokemon", pokemon[0]
        else:
            return DEF_IMP_TERM[imp_terms[0]], imp_terms[0]

    if rep_type == "team":
        if team != "":
            curr_trainer.team = team
            return "NO WAY!!!! ... I am team " + team + " too!!!", team
    if rep_type == "fav":
        if pokemon:
            curr_trainer.fav = pokemon[0]
            facts = find_pokemon_fact(pokemon[0])
            return random.choice(facts), pokemon[0]
        else:
            return "Oh I've never heard of that one before..", ""
    if rep_type == "caught":
        if pokemon:
            if curr_trainer.caught_pokemon != "":
                curr_trainer.caught_pokemon += ","
            curr_trainer.caught_pokemon += ",".join(pokemon)
            target_pokemon = random.choice(pokemon)
            facts = find_pokemon_fact(target_pokemon)
            return random.choice(facts), target_pokemon
        else:
            return "Oh I've never heard of that one before..", ""

    if imp_terms:
        term = imp_terms[0]
        return get_fact_reply(term)

    return get_default_reply(curr_trainer)


def get_fact_reply(term):
    if term == "Berry":
        return random.choice(BERRY), "Berry"
    if term == "Raid":
        return random.choice(RAID), "Raid"
    if term == "Candy":
        return random.choice(CANDY), "Candy"
    if term == "Gym":
        return random.choice(GYM), "Gym"
    if term == "Ball":
        return random.choice(BALL), "Ball"
    if term == "Stardust":
        return random.choice(STARDUST), "Stardust"
    if term == "Eggs":
        return random.choice(EGGS), "Eggs"
    if term == "Research":
        return random.choice(RESEARCH), "Research"
    if term == "Event":
        return random.choice(EVENT), "Event"
    if term == "Type":
        return random.choice(TYPE), "Type"
    if term == "Pokemon":
        return DEF_IMP_TERM[term], term
    if term == "Shiny":
        return DEF_IMP_TERM[term], term
    if term == "Alolan":
        return DEF_IMP_TERM[term], term
    if term == "Regional":
        return DEF_IMP_TERM[term], term


def get_default_options(curr_trainer):
    default_options = ["caught", "reg"]
    if curr_trainer.team == "":
        default_options.append("team")
    if curr_trainer.fav == "":
        default_options.append("fav")
    return default_options


def get_default_reply(curr_trainer):
    default_options = get_default_options(curr_trainer)
    topic = random.choice(default_options)
    if topic == "team":
        return random.choice(CONVO_CARRIER_TEAM), topic
    if topic == "fav":
        return random.choice(CONVO_CARRIER_FAV), topic
    if topic == "caught":
        return random.choice(CONVO_CARRIER_CAUGHT), topic
    else:
        return random.choice(CONVO_CARRIER_REG), topic


def get_shiny_reply(pokemon):
    if pokemon in SHINY_POKEMON:
        return "Yea " + pokemon + " can be shiny!!!", pokemon
    else:
        return "Sadly " + pokemon + " can not be shiny ... Yet!", pokemon


if __name__ == "__main__":
    main()
