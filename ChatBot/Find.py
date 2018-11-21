import spacy
import logging
import Levenshtein
from Info.Pokemon import TEAMS
from Info.Pokemon import POKEMON_AVAIL
from Info.Pokemon import POKEMON_NOT_AVAIL
from Info.Pokemon import SHINY_POKEMON
from Info.Pokemon import REGIONAL_POKEMON
from Info.Pokemon import ALOLA_POKEMON
from Info.Facts import IMP_TERMS
from Info.EggHatches import HATCHES_2K
from Info.EggHatches import HATCHES_5K
from Info.EggHatches import HATCHES_7K
from Info.EggHatches import HATCHES_10K

from Info.PokemonResponses import *

import random
import pickle
import math

nlp = spacy.load('en_core_web_sm')
logging.basicConfig(filename='log_file.log')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def proccess_sentance(sent):
    nlp(sent)
    pronoun = find_pronoun(sent)


def find_pronoun(sent):
    """Given a sentence, find a preferred pronoun to respond with. Returns None if no candidate
    pronoun is found in the input"""
    for word in sent:
        # Disambiguate pronouns
        if word.pos_ == 'PRP' and word.text.lower() == 'you':
            logger.info("Found pronoun: I")
            return 'I'
        elif word.pos_ == 'PRP' and word.text == 'I':
            logger.info("Found pronoun: You")
            return 'You'
    return ""


def find_verb(sent):
    """Pick a candidate verb for the sentence."""
    for word in sent:
        if word.pos_.startswith('VB'):  # This is a verb
            logger.info("Found verb: %s", word.text)
            return word.text
    return ""


def find_name(sent):
    # Given a sentence, find the best candidate Name. Uses Spacy ER
    tags = nlp(sent)

    for entity in tags.ents:
        if entity.text != "Pogo":
            logger.info("Entity %s has been found", entity)
            return str(entity)

    for tag in tags:
        if tag.text != "Pogo" and tag.pos_ == "PROPN":
            logger.info("NNP %s has been found", tag)
            return str(tag)

    return None


def find_noun(sent):
    """Given a sentence, find the best candidate noun."""
    for word in sent:
        if word.pos_ == 'NN':  # This is a noun
            logger.info("Found noun: %s", word.text)
            return word.text
    return ""


def find_adjective(sent):
    """Given a sentence, find the best candidate adjective."""
    for word in sent:
        if word.pos_ == 'JJ':  # This is an adjective
            logger.info("Found adjective: %s", word.text)
            return word.text
    return ""


def find_pokemon(sent):
    """Given a sentence, find if a user mentioned a pokemon."""
    pokemons = []
    tokens = nlp(sent.lower())
    for token in tokens:
        closest = ""
        close_dist = 3
        for pokemon in POKEMON_AVAIL:
            dist = Levenshtein.distance(token.text.lower(), pokemon.lower())
            if dist < close_dist:
                closest = pokemon
                close_dist = dist
        for pokemon in POKEMON_NOT_AVAIL:
            dist = Levenshtein.distance(token.text.lower(), pokemon.lower())
            if dist < close_dist:
                closest = pokemon
                close_dist = dist
            # logger.info("Token %s has distance %d from %s", token, dist, pokemon)
        if close_dist < 3:
            logger.info("Found pokemon: %s", closest)
            pokemons.append(closest)
    return pokemons


def find_imp_term(sent):
    """Given a sentence, find if a user mentioned a important term."""
    imp_terms = []
    tokens = nlp(sent.lower())
    for token in tokens:
        for term in IMP_TERMS:
            dist = Levenshtein.distance(token.lemma_, nlp(term.lower())[0].lemma_)
            logger.info("Token %s has distance %d from %s", token.lemma_, dist, nlp(term.lower())[0].lemma_)
            if dist < 2:
                imp_terms.append(term)
    return imp_terms


def find_team(sent):
    tokens = nlp(sent.lower())
    for token in tokens:
        for team in TEAMS:
            dist = Levenshtein.distance(token.text, team.lower())
            logger.info("Token %s has distance %d from %s", token, dist, team)
            if dist < 3:
                return team
    return ""


def find_pokemon_fact(pokemon):
    # egg hatch, shiny, regional, alola, legendary type, counters
    facts = []
    egg_hatch = find_egg_hatch(pokemon)
    if egg_hatch > 0:
        facts.append(random.choice(EGG_RESPONSES).format(**{'pokemon': pokemon, 'egg_dist': egg_hatch}))
    if pokemon in SHINY_POKEMON:
        facts.append(random.choice(SHINY_RESPONSES).format(**{'pokemon': pokemon}))
    if pokemon in REGIONAL_POKEMON:
        facts.append(random.choice(REGIONAL_RESPONSES).format(**{'pokemon': pokemon}))
    if pokemon in ALOLA_POKEMON:
        facts.append(random.choice(ALOLAN_RESPONSES).format(**{'pokemon': pokemon}))

    with open("./Info/pokedex.pickle", "rb") as pokedex_file:
        pokedex = pickle.load(pokedex_file)
        pok_type = pokedex[pokemon]["type1"]
        if isinstance(pokedex[pokemon]["type2"], str) :
            pok_type += "/" + pokedex[pokemon]["type2"]
        facts.append(random.choice(TYPE_RESPONSES).format(**{'pokemon': pokemon, 'type':pok_type}))

    return facts


def find_egg_hatch(pokemon):
    if pokemon in HATCHES_2K:
        logger.info("Pokemon %s hatches from 2k egg", pokemon)
        return 2
    elif pokemon in HATCHES_5K:
        logger.info("Pokemon %s hatches from 5k egg", pokemon)
        return 5
    elif pokemon in HATCHES_7K:
        logger.info("Pokemon %s hatches from 7k egg", pokemon)
        return 7
    elif pokemon in HATCHES_10K:
        logger.info("Pokemon %s hatches from 10k egg", pokemon)
        return 10
    logger.info("Pokemon %s does not hatch from an egg", pokemon)
    return 0
