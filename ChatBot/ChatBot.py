# Chris Janusa and Nymisha Jahagirdar
# Inspired by BroBot available at https://github.com/lizadaly/brobot/
from __future__ import print_function, unicode_literals
import random
import logging
import os
from textblob import TextBlob
import spacy
from pathlib import Path
import pickle

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
            user_statement = proccess_sentance(input(random.choice(RETURN_TRAINER).format(**{'name': name}) + " btw Go " + trainer.team + "!!!!!!" + "\n> "))
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


def hatches_from(num):
    if num == 2:
        return random.sample(HATCHES_2K, 6)
    if num == 5:
        return random.sample(HATCHES_5K, 6)
    if num == 7:
        return random.sample(HATCHES_7K, 6)
    if num == 10:
        return random.sample(HATCHES_10K, 6)


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

    if pokemon:
        reply = get_shiny_reply(pokemon[0], doj, adj, verb)
        if reply != "":
            return reply
    elif rep_type in ALL_POKEMON:
        reply = get_shiny_reply(rep_type, doj, adj, verb)
        if reply != "":
            return reply

    if is_egg and not pokemon:
        hatch_list = hatches_from(num)
        last = hatch_list.pop()
        return "To name a few: " + ", ".join(hatch_list) + " and " + last + " hatch from " + str(num) + "km eggs", str(num) + "km"

    if imp_terms and "be" in verb:
        if "Type" in imp_terms and pokemon:
            return pokemon[0] + " is a " + find_type(pokemon[0]) + " type pokemon", pokemon[0]
        else:
            return DEF_IMP_TERM[imp_terms[0]], imp_terms[0]

    if rep_type != "" and rep_type != "reg":
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


def get_shiny_reply(pokemon, doj, adj, verb):
    if ('shiny' in doj or 'shiny' in adj) and ('have' in verb or 'be' in verb):
        if pokemon in SHINY_POKEMON:
            return "Yea " + pokemon + " can be shiny!!!", pokemon
        else:
            return "Sadly " + pokemon + " can not be shiny ... Yet!", pokemon
    return ""


if __name__ == "__main__":
    main()
