import spacy
import logging
import Levenshtein
from Info.Pokemon import TEAMS
from Info.Pokemon import POKEMON_AVAIL
from Info.Pokemon import SHINY_POKEMON
from Info.Pokemon import REGIONAL_POKEMON
from Info.Pokemon import ALOLA_POKEMON
from Info.Facts import IMP_TERMS
from Info.EggHatches import HATCHES_2K
from Info.EggHatches import HATCHES_5K
from Info.EggHatches import HATCHES_7K
from Info.EggHatches import HATCHES_10K

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
        for pokemon in POKEMON_AVAIL:
            dist = Levenshtein.distance(token.text, pokemon.lower())
            # logger.info("Token %s has distance %d from %s", token, dist, pokemon)
            if dist < 2:
                pokemons.append(pokemon)
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
    #egg hatch, shiny, regional, alola, legendary type, counters
    facts = []
    egg_hatch = find_egg_hatch(pokemon)
    if egg_hatch > 0:
        facts.append("Did you know " + pokemon + " hatch out of a " + str(egg_hatch) + "km egg?")
    if pokemon in SHINY_POKEMON:
        facts.append("Did you know " + pokemon + " can be shiny?")
    if pokemon in REGIONAL_POKEMON:
        facts.append("Did you know " + pokemon + " is a regional?")
    if pokemon in ALOLA_POKEMON:
        facts.append("Did you know " + pokemon + " can be alolan as well?")
    if facts:
        facts.append("Oh that's interesting..")

    return facts


def find_egg_hatch(pokemon):
    if pokemon in HATCHES_2K:
            return 2
    elif pokemon in HATCHES_5K:
            return 5
    elif pokemon in HATCHES_7K:
            return 7
    elif pokemon in HATCHES_10K:
            return 10
    return 0
