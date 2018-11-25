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
            print(random.choice(RETURN_TRAINER).format(**{'name': name}) + " btw Go " + trainer.team + "!!!!!!")
        else:
            print(random.choice(RETURN_TRAINER).format(**{'name': name}))

    else:
        trainer = Trainer(name)
        trainers[name] = trainer
        print(random.choice(NEW_TRAINER).format(**{'name': name}))

    user_statement = proccess_sentance(
        input("I can answer questions about parts of the game and about specific pokemon."
              "\nEx. \"Can Pichu be shiny?\" or \"What is stardust?\" for a full list say"
              " \"show all\"" + "\n>"))
    rep_type = "ask"
    while not user_statement.isFarewell:
        reply, rep_type = get_reply(user_statement, trainer, rep_type)
        user_statement = proccess_sentance(input(reply + "\n>"))

    print(random.choice(BYE))
    with open(str(pickle_path), "wb") as pickle_file:
        pickle.dump(trainers, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)


def get_reply(parse_obj, curr_trainer, rep_type):
    you = parse_obj.you
    verb = parse_obj.verb
    num = parse_obj.num
    is_num_egg = parse_obj.isEgg
    pokemon = parse_obj.pokemon
    imp_terms = parse_obj.imp_terms
    team = parse_obj.team
    wp = parse_obj.wp
    against = parse_obj.against
    sent = parse_obj.text
    bad = parse_obj.bad
    caught = parse_obj.caught
    about_eggs = parse_obj.about_eggs
    adj = parse_obj.adj
    type = parse_obj.type

    # Maintains topic so if no pokemon are present assume it is referring to previous topic
    if not pokemon and rep_type in ALL_POKEMON:
        pokemon.append(rep_type)

    # Pattern "What are you"/"Who are you"
    if wp != "" and you and not pokemon and not imp_terms and num == -1:
        return random.choice(SELF_REFLECTIVE).format(**{"word": wp}), ""

    # Pattern "What is your favorite pokemon?"
    if you and ("fav" in adj or "favorite" in adj) and "Pokemon" in imp_terms:
        if curr_trainer.fav == "":
            return "My " + adj[0] + " Pokemon is Chimchar", "Chimchar"
        else:
            return "My " + adj[0] + " Pokemon is Chimchar but your " + adj[
                0] + " " + curr_trainer.fav + " is really cool too", "Chimchar"

    # Pattern "What type of pokemon are you?"
    if you and "Pokemon" in imp_terms and "Type" in imp_terms and "be" in verb:
        if curr_trainer.fav != "":
            return "I would def be a " + find_type(curr_trainer.fav) + " type pokemon just like your favorite", ""
        else:
            return "That's a tough question but if I had to choose right now I would say I'm a " + \
                   random.choice(POKEMON_TYPES) + " type!", ""

    # Pattern "What team are you"/"Are you Mystic"
    if you and "be" in verb and ("Team" in imp_terms or team != ""):
        if curr_trainer.team == "":
            return "I feel like this is a trap... You tell me your team first!", "team"
        if team != "":
            if curr_trainer.team == team:
                return "You know I am team " + team + " till the day I die!!!!", ""
            else:
                return "How dare you even think I would associate with those " + team + " scum", ""
        else:
            return "I am a part of the best team in the world... Team " + curr_trainer.team + "!!!!!!!", ""

    # Pattern "Show all"
    if rep_type == "ask" and "show" in verb:
        if curr_trainer.fav == "":
            pokemon = "Pikachu"
        else:
            pokemon = curr_trainer.fav
        if curr_trainer.team == "":
            team = "Mystic"
        else:
            team = curr_trainer.team
        imp_term = "Stardust"
        return "Can {pokemon} be shiny?\nWhat is {Imp_term} used for?\nWhat can hatch from a 2km egg?" \
               "\nWhat pokemon is #35?\nDoes {pokemon} have an alolan form?\nIs {pokemon} a regional?" \
               "\nWhat type is {pokemon}?\nWhat team are you?\nPogo are you {team}?" \
               "\nWhat type of pokemon are you?\nWhat is your favorite pokemon?\nWhat can a {pokemon} be hatched from?" \
               "\nWhat generation is {pokemon}?\nWhat is strong against {pokemon}?".format(**{'pokemon': pokemon, 'Imp_term': imp_term, "team": team}), 'ask'

    # Pattern "What can I ask you?"
    if you and "ask" in verb:
        return "I can answer questions about parts of the game and about specific pokemon.\nEx. \"Can Pichu be shiny\" " \
               "or \"What is stardust\" for a full list say \"show all\"", "ask"

    # Pattern "Does {pokemon} have an Alolan form?"
    if ("be" in verb or "have" in verb) and pokemon and "Alolan" in imp_terms and "Eggs" not in imp_terms:
        if pokemon[0] in ALOLA_POKEMON:
            return pokemon[0] + " does have an Alolan form", pokemon[0]
        else:
            return "Nope, " + pokemon[0] + " doesn't have an Alolan form", pokemon[0]

    if ("be" in verb or "have" in verb) and pokemon and "Regional" in imp_terms:
        if pokemon[0] in REGIONAL_POKEMON:
            return pokemon[0] + " is a regional pokemon", pokemon[0]
        else:
            return "Nope, " + pokemon[0] + " is available all over the world", pokemon[0]

    # Pattern "What pokemon is {num}?
    if ("be" in verb or "have" in verb) and num != -1:
        pokemon = get_num_pokemon(num)
        if pokemon != "":
            return "#" + str(num) + " is " + pokemon, pokemon

    # Pattern "Can {pokemon} be shiny?"
    if pokemon and "Shiny" in imp_terms and ("be" in verb or "have" in verb or "hatch" in verb):
        return get_shiny_reply(pokemon[0])

    if pokemon and "Generation" in imp_terms and "be" in verb:
        return get_generation_reply(pokemon[0]), pokemon[0]

    # Pattern "What hatches from {num} egg?"
    if is_num_egg and not pokemon:
        hatch_list = hatches_from(num, curr_trainer.fav)
        last = hatch_list.pop()
        return "To name a few: " + ", ".join(hatch_list) + " and " + last + " hatch from " + str(num) + "km eggs", str(
            num) + "km"

    # Pattern "can a {pokemon} hatch from an egg"
    if about_eggs and pokemon:
        isAlolan = "Alolan" in imp_terms and pokemon[0] in ALOLA_POKEMON
        egg = find_egg_hatch(pokemon[0], isAlolan)
        if isAlolan:
            return "Alolan " + pokemon[0] + " can hatch from " + str(egg) + "km eggs.", pokemon[0]
        elif egg == 0:
            return "No, they do not hatch from eggs.", pokemon[0]
        else:
            if num > 0 and num != egg:
                return "No, " + pokemon[0] + " does not hatch from " + str(
                    num) + "km eggs but it does hatch from " + str(egg) + "km eggs!", pokemon[0]
            return pokemon[0] + " can hatch from " + str(egg) + "km eggs.", pokemon[0]

    # Pattern "What is strong against {pokemon}?"
    if against:
        if bad:
            if "Type" in imp_terms:
                return find_type_counters(type[0], 0), ""
            elif pokemon:
                return find_counters(curr_trainer, pokemon[0], 0), pokemon[0]

        else:
            if "Type" in imp_terms:
                return find_type_counters(type[0] , 1), ""
            elif pokemon:
                return find_counters(curr_trainer, pokemon[0], 1), pokemon[0]

    if "caught" in sent and you:
        if pokemon:
            target_pokemon = random.choice(pokemon)
            return random.choice(
                ["Yes, I have caught them!", "No, I have not caught a " + target_pokemon + " yet.."]), target_pokemon
        else:
            return "Oh I've never heard of that one before..", ""

    # Pattern "I caught a {pokemon}"
    if caught:
        if pokemon:
            if "I" or "i" in sent:
                if curr_trainer.caught_pokemon != "":
                    curr_trainer.caught_pokemon += ","
                curr_trainer.caught_pokemon += ",".join(pokemon)
                target_pokemon = random.choice(pokemon)
                facts = find_pokemon_fact(target_pokemon)
                return random.choice(facts), target_pokemon
        else:
            return "Oh I've never heard of that one before..", ""

    # Pattern "What egg does {pokemon} hatch from?" / "Does {pokemon} hatch from {num} egg
    if "Eggs" in imp_terms and pokemon:
        if not is_num_egg:
            return get_egg_hatch_reply(pokemon[0], "Alolan" in imp_terms and pokemon[0] in ALOLA_POKEMON), pokemon[0]
        else:
            return get_hatches_from_reply(num, pokemon[0], "Alolan" in imp_terms and pokemon[0] in ALOLA_POKEMON), pokemon[0]

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
    if term == "Generation":
        return random.choice(TYPE), "Generation"
    if term == "Pokemon":
        return DEF_IMP_TERM[term], term
    if term == "Shiny":
        return DEF_IMP_TERM[term], term
    if term == "Alolan":
        return DEF_IMP_TERM[term], term
    if term == "Regional":
        return DEF_IMP_TERM[term], term
    if term == "Team":
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


def get_hatches_from_reply(num, pokemon, isAlolan):
    if num == 2:
        hatches = HATCHES_2K
    elif num == 5:
        hatches = HATCHES_5K
    elif num == 7:
        if isAlolan:
            return "Yes Alolan " + pokemon + " does hatch from " + str(num) + "km eggs!!!"
        hatches = HATCHES_7K
    else:
        hatches = HATCHES_10K

    if pokemon in hatches:
        return "Yes " + pokemon + " does hatch from " + str(num) + "km eggs!!!"
    elif find_egg_hatch(pokemon, isAlolan) != 0:
        return "No " + pokemon + " does not hatch from " + str(num) + "km eggs but it does hatch from " + str(
            find_egg_hatch(pokemon, isAlolan)) + "km eggs!"
    else:
        return "No " + pokemon + " does not hatch from eggs"


def get_egg_hatch_reply(pokemon, isAlolan):
    if pokemon in HATCHES_2K:
        return pokemon + " hatches from 2km eggs"
    elif pokemon in HATCHES_5K:
        return pokemon + " hatches from 5km eggs"
    elif pokemon in HATCHES_7K:
        return pokemon + " hatches from 7km eggs"
    elif isAlolan:
        return "Alolan " + pokemon + " hatches from 7km eggs"
    elif pokemon in HATCHES_10K:
        return pokemon + " hatches from 10km eggs"
    return pokemon + " does not hatch from any eggs sadly"


def get_num_pokemon(num):
    with open("./Info/pokedex.pickle", "rb") as pokedex_file:
        pokedex = pickle.load(pokedex_file)
        for key, value in pokedex.items():
            if value["pokedex_number"] == num:
                return value["name"]
    return ""


def get_generation_reply(pokemon):
    with open("./Info/pokedex.pickle", "rb") as pokedex_file:
        pokedex = pickle.load(pokedex_file)
        return pokemon + " is a part of generation " + str(pokedex[pokemon]["generation"])


if __name__ == "__main__":
    main()
