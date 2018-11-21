import spacy
import logging
import Levenshtein
from Info.Pokemon import TEAMS

nlp = spacy.load('en_core_web_sm')
logging.basicConfig(filename='log_file.log')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def find_pronoun(sent):
    """Given a sentence, find a preferred pronoun to respond with. Returns None if no candidate
    pronoun is found in the input"""
    pronoun = None

    for word, part_of_speech in sent.pos_tags:
        # Disambiguate pronouns
        if part_of_speech == 'PRP' and word.lower() == 'you':
            pronoun = 'I'
        elif part_of_speech == 'PRP' and word == 'I':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'You'
    return pronoun


def find_verb(sent):
    """Pick a candidate verb for the sentence."""
    verb = None
    pos = None
    for word, part_of_speech in sent.pos_tags:
        if part_of_speech.startswith('VB'):  # This is a verb
            verb = word
            pos = part_of_speech
            break
    return verb, pos


def find_name(sent):
    # Given a sentence, find the best candidate Name. Uses Spacy ER

    tags = nlp(sent)

    for tag in tags:
        if tag.text != "Pogo" and tags[0].pos_ == "PROPN":
            logger.info("NNP %s has been found", tag)
            return str(tag)

    return None


def find_noun(sent):
    """Given a sentence, find the best candidate noun."""
    noun = None

    if not noun:
        for w, p in sent.pos_tags:
            if p == 'NN':  # This is a noun
                noun = w
                break
    if noun:
        logger.info("Found noun: %s", noun)

    return noun


def find_adjective(sent):
    """Given a sentence, find the best candidate adjective."""
    adj = None
    for w, p in sent.pos_tags:
        if p == 'JJ':  # This is an adjective
            adj = w
            break
    return adj


def find_pokemon(sent):
    """Given a sentence, find if a user mentioned a pokemon."""
    pokemon = None


def find_team(sent):
    tokens = nlp(sent.lower())
    for token in tokens:
        for team in TEAMS:
            dist = Levenshtein.distance(token.text, team.lower())
            logger.info("Token %s has distance %d from %s", token, dist, team)
            if dist < 3:
                return team
    return ""