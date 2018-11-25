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


def proccess_sentance(sent):
    nlp_sent = nlp(sent)
    parse = Parsed()
    parse.you = find_you(nlp_sent)
    parse.verb = find_verb(nlp_sent)
    parse.name = find_name(nlp_sent)
    parse.against = is_against(nlp_sent)
    parse.good = is_good(nlp_sent)
    parse.bad = is_bad(nlp_sent)
    parse.about_eggs = find_about_eggs(nlp_sent)
    parse.caught = find_caught(nlp_sent)
    parse.type = find_mentioned_type(nlp_sent)
    parse.pokemon = find_pokemon(nlp_sent)

    if "mr. mime" in sent.lower():
        parse.pokemon.append("Mr. Mime")
    if "mr mime" in sent.lower():
        parse.pokemon.append("Mr. Mime")
    if "mime jr" in sent.lower():
        parse.pokemon.append("Mime Jr.")
    if "ho-oh" in sent.lower():
        parse.pokemon.append("Ho-Oh")
    parse.imp_terms = find_imp_term(nlp_sent)
    parse.team = find_team(nlp_sent)
    parse.isFarewell = is_farewell(nlp_sent)
    parse.wp = find_wp(nlp_sent)
    num, is_egg_num = find_egg_num(nlp_sent)
    parse.num = num
    parse.isEgg = is_egg_num
    parse.text = sent
    parse.adj = find_adjective(nlp_sent)
    logger.info("Adjectives: %s Verbs: %s Names: %s Pokemon: %s Imp Terms: %s Team: %s Num: %d IsEgg: %r HasYou: %r WP: %s",
                ", ".join(parse.adj), ", ".join(parse.verb), parse.name, ", ".join(parse.pokemon), ", ".join(parse.imp_terms),
                parse.team, num, is_egg_num, parse.you, parse.wp)

    return parse


def find_verb(sent):
    """Pick a candidate verb for the sentence."""
    verbs = []
    for word in sent:
        logger.info("Word: %s Pos: %s", word.text, word.tag_)
        if word.tag_.startswith('VB'):  # This is a verb
            #logger.info("Found verb: %s Lemma: %s", word.text, word.lemma_)
            if word.text == "'s":
                verbs.append("be")
            else:
                verbs.append(str(word.lemma_))
    return verbs


def find_wp(sent):
    """Pick a candidate verb for the sentence."""
    for word in sent:
        if word.tag_ == "WP":  # This is a verb
            return str(word)
    return ""

def find_adjective(sent):
    """Given a sentence, find the best candidate adjective."""
    adjs = []
    for word in sent:
        if word.tag_ == 'JJ':  # This is an adjective
            logger.info("Found adj: %s Lemma: %s", word.text, word.lemma_)
            adjs.append(word.lemma_)
    return adjs


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


def find_pronoun(sent):
    """Given a sentence, find a preferred pronoun to respond with. Returns None if no candidate
    pronoun is found in the input"""
    pronouns = []
    for word in sent:
        # Disambiguate pronouns
        if word.tag_ == 'PRP' and (word.text.lower() == 'you' or word.text.lower() == 'your'):
            logger.info("Found pronoun: I")
            pronouns.append('I')
        elif word.tag_ == 'PRP' and word.text == 'I':
            logger.info("Found pronoun: You")
            pronouns.append('You')
    return ""


def find_you(sent):
    for word in sent:
        if word.text.lower() == 'you' or word.text.lower() == 'your' or word.text.lower() == 'pogo':
            return True
    return False


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

def is_farewell(sent):
    for token in sent:
        if "bye" in str(token):
            return True
    return False

def is_against(sent):
    for word in sent:
        if word.lemma_ == "against" or word.lemma_ == "counter":
            return True
    return False


def find_imp_term(sent):
    """Given a sentence, find if a user mentioned a important term."""
    imp_terms = []
    for token in sent:
        for term in IMP_TERMS:
            dist = Levenshtein.distance(token.lemma_, nlp(term.lower())[0].lemma_)

            # logger.info("Token %s has distance %d from %s", token.lemma_, dist, nlp(term.lower())[0].lemma_)
            if len(token.text) < 5:
                if dist == 0:
                    imp_terms.append(term)
                if token.text.lower() == "gen":
                    imp_terms.append("Generation")
            elif dist < 2:
                if term == "Pokeball":
                    imp_terms.append("Ball")
                else:
                    imp_terms.append(term)
    return imp_terms


def find_team(sent):
    for token in sent:
        for team in TEAMS:
            dist = Levenshtein.distance(token.text.lower(), team.lower())
            # logger.info("Token %s has distance %d from %s", token, dist, team)

            if dist < 3:
                return team
    return ""

def find_egg_num(sent):
    num = -1
    is_egg_num = False
    for word in sent:
        if is_egg_num and word.lemma_ == "egg":
            return num, True

        if word.pos_ == "NUM" and word.shape_.startswith("d"):
            num = int(word.text.split("k")[0])
            if num == 2 or num == 5 or num == 7 or num == 10:
                is_egg_num = True
    return num, False

def find_about_eggs(sent):
    for word in sent:
        if word.lemma_ == "egg" or word.lemma_ == "hatch":
            return True
    return False

def is_good(sent):
    for word in sent:
        if word.lemma_ == "good" or word.lemma_ == "strong":
            return True
    return False

def is_bad(sent):
    for word in sent:
        if word.lemma_ == "bad" or word.lemma_ == "weak":
            return True
    return False


def find_caught(sent):
    for word in sent:
        if word.lemma_ == "catch":
            return True
    return False


def find_egg_hatch(pokemon, isAlolan):
    if pokemon in HATCHES_2K:
        logger.info("Pokemon %s hatches from 2k egg", pokemon)
        return 2
    elif pokemon in HATCHES_5K:
        logger.info("Pokemon %s hatches from 5k egg", pokemon)
        return 5
    elif pokemon in HATCHES_7K or isAlolan:
        logger.info("Pokemon %s hatches from 7k egg", pokemon)
        return 7
    elif pokemon in HATCHES_10K:
        logger.info("Pokemon %s hatches from 10k egg", pokemon)
        return 10
    logger.info("Pokemon %s does not hatch from an egg", pokemon)
    return 0

def find_pokemon(sent):
    """Given a sentence, find if a user mentioned a pokemon."""
    pokemons = []

    for token in sent:
        if token.text.lower() == 'shiny' or token.text.lower() == "comes" or token.text.lower() == "counter":
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
        if closest != "":
            logger.info("Found pokemon: %s", closest)
            pokemons.append(closest)
    return pokemons

def find_mentioned_type(sent):
    """Given a sentence, find if a user mentioned a pokemon."""
    types = []

    for token in sent:
        closest = ""
        close_dist = 2
        if len(token.text) < 5:
            closest = ""
            close_dist = 1
        for type in POKEMON_TYPES:
            dist = Levenshtein.distance(token.text.lower(), type.lower())
            if dist < close_dist:
                closest = type
                close_dist = dist
        if closest != "":
            logger.info("Found type: %s", closest)
            types.append(closest.capitalize())
    return types

def find_type(pokemon):
    with open("./Info/pokedex.pickle", "rb") as pokedex_file:
        pokedex = pickle.load(pokedex_file)
        pok_type = pokedex[pokemon]["type1"]
        if isinstance(pokedex[pokemon]["type2"], str):
            pok_type += "/" + pokedex[pokemon]["type2"]

        return pok_type


def find_pokemon_fact(pokemon):
    facts = []
    egg_hatch = find_egg_hatch(pokemon, False)
    if egg_hatch > 0:
        facts.append(random.choice(EGG_RESPONSES).format(**{'pokemon': pokemon, 'egg_dist': egg_hatch}))
    if pokemon in SHINY_POKEMON:
        facts.append(random.choice(SHINY_RESPONSES).format(**{'pokemon': pokemon}))
    if pokemon in REGIONAL_POKEMON:
        facts.append(random.choice(REGIONAL_RESPONSES).format(**{'pokemon': pokemon}))
    if pokemon in ALOLA_POKEMON:
        facts.append(random.choice(ALOLAN_RESPONSES).format(**{'pokemon': pokemon}))

    pok_type = find_type(pokemon)
    facts.append(random.choice(TYPE_RESPONSES).format(**{'pokemon': pokemon, 'type':pok_type}))

    strong_against, weak_against = find_against_strength(pokemon)
    strong_last = strong_against.pop()
    weak_last = weak_against.pop()
    strong_string = ", ".join(strong_against) + ", and " + strong_last
    weak_string = ", ".join(weak_against) + ", and " + weak_last
    facts.append(random.choice(AGAINST_TYPE_RESPONSES).format(**{'pokemon': pokemon, 'strong_type':strong_string, 'weak_type':weak_string}))

    return facts

def find_against_strength(pokemon):
    with open("./Info/pokedex.pickle", "rb") as pokedex_file:
        pokedex = pickle.load(pokedex_file)
        strong_against = []
        weak_against = []

        for against_type in TYPES:
            if against_type != pokedex[pokemon]["type1"] and against_type != pokedex[pokemon]["type2"]:
                if pokedex[pokemon][against_type] < 1:
                        if against_type == "fight":
                            strong_against.append("fighting")
                        else:
                            strong_against.append(against_type)
                if pokedex[pokemon][against_type] > 1:
                    if against_type == "fight":
                        weak_against.append("fighting")
                    else:
                        weak_against.append(against_type)

        return strong_against, weak_against


def find_type_counters(type, good_or_bad):
    if good_or_bad == 1:
        file_name = "./Info/weaktypecounters.pickle"
        reply = type + " is weakest against the following types: "
    else:
        file_name = "./Info/strongtypecounters.pickle"
        reply = type + " is strongest against the following types: "
    with open(file_name, "rb") as counters_file:
        counters = pickle.load(counters_file)
        reply += counters[type.upper()]

    return reply


def find_caught_counters(trainer, against_types):
    caught_counters = []

    #strong_against, weak_against = find_against_strength(target_mon)
    caught_pokemons = trainer.caught_pokemon.split(",")
    if trainer.caught_pokemon == "":
        return ""
    with open("./Info/pokedex.pickle", "rb") as pokedex_file:
        pokedex = pickle.load(pokedex_file)
        for search_type in against_types:
            for pokemon in caught_pokemons:
                if (search_type == pokedex[pokemon]["type1"] or search_type == pokedex[pokemon]["type2"]) and pokemon not in caught_counters:
                    caught_counters.append(pokemon)

    if len(caught_counters) > 1:
        last = caught_counters.pop()
        ret_string = ", ".join(caught_counters) + ", and " + last
        return ret_string
    elif caught_counters:
        return caught_counters[0]
    else: return ""

def find_counters(trainer, pokemon, good_or_bad):
    strong_against, weak_against = find_against_strength(pokemon)

    if good_or_bad == 1:
        caught_counters = find_caught_counters(trainer, weak_against)
        if len(weak_against) > 1:
            weak_last = weak_against.pop()
            weak_string = ", ".join(weak_against) + ", and " + weak_last
        else:
            weak_string = weak_against[0]
        reply = pokemon + " is weakest against " + weak_string + " types."
    else:
        caught_counters = find_caught_counters(trainer, strong_against)
        if len(strong_against) > 1:
            strong_last = strong_against.pop()
            strong_string = ", ".join(strong_against) + ", and " + strong_last
        else:
            strong_string = strong_against[0]
        reply = pokemon + " is strongest against " + strong_string + " types."
    if caught_counters != "":
        if good_or_bad == 1:
            reply += "\nYou could use the "
        else:
            reply += "\nYou should avoid the "
        reply += caught_counters + " pokemon that you caught earlier to fight it!"

    return reply





