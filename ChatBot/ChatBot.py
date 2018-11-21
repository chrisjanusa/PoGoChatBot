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

from SentanceProccessing import starts_with_vowel

from Find import find_name
from Find import find_team
from Find import find_pokemon
from Find import find_imp_term
from Find import find_pokemon_fact

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
    user_statement = input(random.choice(INRODUCTION) + "\n> ")
    name = find_name(user_statement)

    while name is None:
        blob = TextBlob(user_statement)
        if blob.sentiment.polarity < 0.1:
            user_statement = input(random.choice(NO_NAME_SASSY) + "\n> ")
        else:
            user_statement = input(random.choice(NO_NAME) + "\n> ")
        name = find_name(user_statement)

    pickle_path = Path("dict.pickle")
    if pickle_path.is_file():
        pickle_in = open(str(pickle_path), "rb")
        trainers = pickle.load(pickle_in)
    else:
        trainers = {}

    if name in trainers:
        trainer = trainers[name]
        if trainer.team != "":
            print("Go " + trainer.team + "!!!!!!")
        user_statement = input(random.choice(RETURN_TRAINER).format(**{'name': name}) + "\n> ")
    else:
        trainer = Trainer(name)
        trainers[name] = trainer
        user_statement = input(random.choice(NEW_TRAINER).format(**{'name': name}) + "\n> ")

    rep_type = ""
    while "bye" not in user_statement.lower():
        reply, rep_type = get_reply(user_statement, trainer, rep_type)
        user_statement = input(reply + "\n>")

    print(random.choice(BYE))
    pickle.dump(trainers, open(str(pickle_path), "wb"))


def construct_response(pronoun, noun, verb):
    """No special cases matched, so we're going to try to construct a full sentence that uses as much
    of the user's input as possible"""
    resp = []

    if pronoun:
        resp.append(pronoun)

    # We always respond in the present tense, and the pronoun will always either be a passthrough
    # from the user, or 'you' or 'I', in which case we might need to change the tense for some
    # irregular verbs.
    if verb:
        verb_word = verb[0]
        if verb_word in ('be', 'am', 'is', "'m"):  # This would be an excellent place to use lemmas!
            if pronoun.lower() == 'you':
                # The bot will always tell the person they aren't whatever they said they were
                resp.append("aren't really")
            else:
                resp.append(verb_word)
    if noun:
        pronoun = "an" if starts_with_vowel(noun) else "a"
        resp.append(pronoun + " " + noun)

    resp.append(random.choice(("tho", "bro", "lol", "bruh", "smh", "")))

    return " ".join(resp)


def get_reply(user_statement, curr_trainer, rep_type):
    if rep_type != "" and rep_type != "reg":
        if rep_type == "team":
            team = find_team(user_statement)
            if team != "":
                curr_trainer.team = team
                return "NO WAY!!!! ... I am team " + team + " too!!!", ""
        if rep_type == "fav":
            pokemon = find_pokemon(user_statement)
            if pokemon != []:
                curr_trainer.fav = pokemon[0]
                facts = find_pokemon_fact(pokemon[0])
                return random.choice(facts), ""
            else:
                return "Oh I've never heard of that one before..", ""
        if rep_type == "caught":
            pokemon = find_pokemon(user_statement)
            if pokemon != []:
                curr_trainer.fav = pokemon[0]
                facts = find_pokemon_fact(pokemon[0])
                return random.choice(facts), ""
            else:
                return "Oh I've never heard of that one before..", ""
    else:
        imp_terms = find_imp_term(user_statement)
        if imp_terms !=[]:
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
    if curr_trainer.favorite_pokemon == "":
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
