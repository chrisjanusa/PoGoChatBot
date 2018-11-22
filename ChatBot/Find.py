import spacy
import logging
import Levenshtein
from Info.Pokemon import *
from Info.Facts import IMP_TERMS
from Info.EggHatches import *

from Info.PokemonResponses import *

from SentanceParsed import Parsed

import random
import pickle

nlp = spacy.load('en_core_web_sm')
logging.basicConfig(filename='log_file.log')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def isFarewell(sent):
    for token in sent:
        if "bye" in str(token):
            return True
    return False


def proccess_sentance(sent):
    nlp_sent = nlp(sent)
    parse = Parsed()
    parse.pronoun = find_pronoun(nlp_sent)
    parse.adj = find_adjective(nlp_sent)
    parse.subj = find_subj(nlp_sent)
    parse.verb = find_verb(nlp_sent)
    parse.doj = find_doj(nlp_sent)
    parse.name = find_name(nlp_sent)
    parse.pokemon = find_pokemon(nlp_sent)
    parse.imp_terms = find_imp_term(nlp_sent)
    parse.team = find_team(nlp_sent)
    parse.isFarewell = isFarewell(nlp_sent)
    parse.text = sent

    logger.info("Dobj: %s Pronouns: %s Adjs: %s Subjs: %s Verbs: %s Names: %s Pokemon: %s Imp Terms: %s Team: %s",
                ", ".join(parse.doj), "".join(parse.pronoun), ", ".join(parse.adj), ", ".join(parse.subj), ", ".join(parse.verb),
                parse.name, ", ".join(parse.pokemon), ", ".join(parse.imp_terms), parse.team)

    return parse


def find_pronoun(sent):
    """Given a sentence, find a preferred pronoun to respond with. Returns None if no candidate
    pronoun is found in the input"""
    pronouns = []
    for word in sent:
        # Disambiguate pronouns
        if word.tag_ == 'PRP' and word.text.lower() == 'you':
            logger.info("Found pronoun: I")
            pronouns.append('I')
        elif word.tag_ == 'PRP' and word.text == 'I':
            logger.info("Found pronoun: You")
            pronouns.append('You')
    return ""


def find_verb(sent):
    """Pick a candidate verb for the sentence."""
    verbs = []
    for word in sent:
        if word.tag_.startswith('VB'):  # This is a verb
            logger.info("Found verb: %s Lemma: %s", word.text, word.lemma_)
            verbs.append(str(word.lemma_))
    return verbs


def find_name(sent):
    # Given a sentence, find the best candidate Name. Uses Spacy ER
    for entity in sent.ents:
        if entity.text != "Pogo":
            logger.info("Entity %s has been found", entity)
            return str(entity)

    for tag in sent:
        if tag.text != "Pogo" and tag.pos_ == "PROPN":
            logger.info("NNP %s has been found", tag)
            return str(tag)

    return ""


def find_subj(sent):
    """Given a sentence, find the best candidate noun."""
    subjs = []
    for word in sent:
        if word.dep_ == 'subj':  # This is a noun
            logger.info("Found subject: %s Lemma: %s", word.text, word.lemma_)
            subjs.append(str(word.lemma_))
    return subjs


def find_doj(sent):
    """Given a sentence, find the best candidate noun."""
    dobjs = []
    for word in sent:
        if word.dep_ == 'dobj':  # This is a noun
            logger.info("Found dobj: %s Lemma: %s", word.text, word.lemma_)
            dobjs.append(str(word.lemma_))
    return dobjs


def find_adjective(sent):
    """Given a sentence, find the best candidate adjective."""
    adjs = []
    for word in sent:
        if word.tag_ == 'JJ':  # This is an adjective
            logger.info("Found adj: %s Lemma: %s", word.text, word.lemma_)
            adjs.append(word.lemma_)
    return adjs


def find_pokemon(sent):
    """Given a sentence, find if a user mentioned a pokemon."""
    pokemons = []
    for token in sent:
        if token.text == 'shiny':
            continue

        closest = ""
        close_dist = 3
        if len(token.text) < 5:
            closest = ""
            close_dist = 1
        for pokemon in ALL_POKEMON:
            dist = Levenshtein.distance(token.text.lower(), pokemon.lower())
            if dist < close_dist:
                closest = pokemon
                close_dist = dist
            # logger.info("Token %s has distance %d from %s", token, dist, pokemon)
        if closest != "":
            logger.info("Found pokemon: %s", closest)
            pokemons.append(closest)
    return pokemons


def find_imp_term(sent):
    """Given a sentence, find if a user mentioned a important term."""
    imp_terms = []
    for token in sent:
        for term in IMP_TERMS:
            dist = Levenshtein.distance(token.lemma_, nlp(term.lower())[0].lemma_)
            logger.info("Token %s has distance %d from %s", token.lemma_, dist, nlp(term.lower())[0].lemma_)
            if dist < 2:
                if term == "Pokeball":
                    imp_terms.append("Ball")
                else:
                    imp_terms.append(term)
    return imp_terms


def find_team(sent):
    for token in sent:
        for team in TEAMS:
            dist = Levenshtein.distance(token.text.lower(), team.lower())
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
        strong_against = ""
        weak_against = ""
        # if pokedex[pokemon] != "":
        if isinstance(pokedex[pokemon]["type2"], str):
            pok_type += "/" + pokedex[pokemon]["type2"]
        facts.append(random.choice(TYPE_RESPONSES).format(**{'pokemon': pokemon, 'type':pok_type}))

        for against_type in TYPES:
            if against_type != pokedex[pokemon]["type1"] and against_type != pokedex[pokemon]["type2"]:
                if pokedex[pokemon][against_type] < 1:
                    if strong_against == "":
                        strong_against = against_type
                    else:
                        strong_against += ", " + against_type
                if pokedex[pokemon][against_type] > 1:
                    if weak_against == "":
                        weak_against = against_type
                    else:
                        weak_against += ", " + against_type
        facts.append(random.choice(AGAINST_TYPE_RESPONSES).format(**{'pokemon': pokemon, 'strong_type':strong_against, 'weak_type':weak_against}))

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


def find_type(pokemon):
    with open("./Info/pokedex.pickle", "rb") as pokedex_file:
        pokedex = pickle.load(pokedex_file)
        pok_type = pokedex[pokemon]["type1"]
        if isinstance(pokedex[pokemon]["type2"], str):
            pok_type += "/" + pokedex[pokemon]["type2"]

        return pok_type
