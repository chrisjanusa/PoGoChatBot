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

from Info.GenericResponses import INRODUCTION
from Info.GenericResponses import NO_NAME_SASSY
from Info.GenericResponses import NEW_TRAINER
from Info.GenericResponses import RETURN_TRAINER
from Info.GenericResponses import NO_NAME
from Info.GenericResponses import CONVO_CARRIER_CAUGHT
from Info.GenericResponses import CONVO_CARRIER_FAV
from Info.GenericResponses import CONVO_CARRIER_REG
from Info.GenericResponses import CONVO_CARRIER_TEAM
from Info.GenericResponses import BYE

from Info.Facts import BERRY
from Info.Facts import RAID
from Info.Facts import CANDY
from Info.Facts import GYM
from Info.Facts import BALL
from Info.Facts import STARDUST
from Info.Facts import EGGS
from Info.Facts import RESEARCH
from Info.Facts import EVENT
from Info.Facts import TYPE

from Trainer import Trainer

nlp = spacy.load('en_core_web_sm')
os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'
logging.basicConfig(filename='log_file.log')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main():
    user_statement = proccess_sentance(input(random.choice(INRODUCTION) + "\n> "))

    while user_statement.name == "":
        blob = TextBlob(user_statement)
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


def get_reply(parse_obj, curr_trainer, rep_type):
    pronoun = parse_obj.pronoun
    adj = parse_obj.adj
    noun = parse_obj.noun
    verb = parse_obj.verb
    name = parse_obj.name
    pokemon = parse_obj.pokemon
    imp_terms = parse_obj.imp_terms
    team = parse_obj.team

    if rep_type != "" and rep_type != "reg":
        if rep_type == "team":
            if team != "":
                curr_trainer.team = team
                return "NO WAY!!!! ... I am team " + team + " too!!!", ""
        if rep_type == "fav":
            if pokemon:
                curr_trainer.fav = pokemon[0]
                facts = find_pokemon_fact(pokemon[0])
                return random.choice(facts), ""
            else:
                return "Oh I've never heard of that one before..", ""
        if rep_type == "caught":
            if pokemon:
                if curr_trainer.caught_pokemon != "":
                    curr_trainer.caught_pokemon += ","
                curr_trainer.caught_pokemon += ",".join(pokemon)
                facts = find_pokemon_fact(random.choice(pokemon))
                return random.choice(facts), ""
            else:
                return "Oh I've never heard of that one before..", ""
    else:
        if imp_terms:
            term = imp_terms[0]
            return get_fact_reply(term)

    return get_default_reply(curr_trainer)


def get_fact_reply(term):
    if term == "Berry":
        return random.choice(BERRY), ""
    if term == "Raid":
        return random.choice(RAID), ""
    if term == "Candy":
        return random.choice(CANDY), ""
    if term == "Gym":
        return random.choice(GYM), ""
    if term == "Ball":
        return random.choice(BALL), ""
    if term == "Stardust":
        return random.choice(STARDUST), ""
    if term == "Eggs":
        return random.choice(EGGS), ""
    if term == "Research":
        return random.choice(RESEARCH), ""
    if term == "Event":
        return random.choice(EVENT), ""
    if term == "Type":
        return random.choice(TYPE), ""


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


if __name__ == "__main__":
    main()
