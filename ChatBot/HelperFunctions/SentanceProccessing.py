from Info.GenericResponses import GREETING_KEYWORDS
from Info.GenericResponses import GREETING_RESPONSES
from Info.GenericResponses import SELF_VERBS_WITH_NOUN_CAPS_PLURAL
from Info.GenericResponses import SELF_VERBS_WITH_NOUN_LOWER
from Info.GenericResponses import SELF_VERBS_WITH_ADJECTIVE

from HelperFunctions.Find import find_pronoun
from HelperFunctions.Find import find_adjective
from HelperFunctions.Find import find_noun
from HelperFunctions.Find import find_verb

from Info.BadWords import FILTER_WORDS

from Classes.Exceptions import UnacceptableUtteranceException

from ExternalFiles import Config

import random
import logging

logging.basicConfig(filename=Config.LOG_FILE)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def check_for_greeting(sentence):
    """If any of the words in the user's input was a greeting, return a greeting response"""
    for word in sentence.words:
        if word.lower() in GREETING_KEYWORDS:
            return random.choice(GREETING_RESPONSES)


def starts_with_vowel(word):
    """Check for pronoun compability -- 'a' vs. 'an'"""
    return True if word[0] in 'aeiou' else False


def check_for_comment_about_bot(pronoun, noun, adjective):
    """Check if the user's input was about the bot itself, in which case try to fashion a response
    that feels right based on their input. Returns the new best sentence, or None."""
    resp = None
    if pronoun == 'I' and (noun or adjective):
        if noun:
            if random.choice((True, False)):
                resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(
                    **{'noun': noun.pluralize().capitalize()})
            else:
                resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
        else:
            resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
    return resp


def find_candidate_parts_of_speech(parsed):
    """Given a parsed input, find the best pronoun, direct noun, adjective, and verb to match their input.
    Returns a tuple of pronoun, noun, adjective, verb any of which may be None if there was no good match"""
    pronoun = None
    noun = None
    adjective = None
    verb = None
    for sent in parsed.sentences:
        pronoun = find_pronoun(sent)
        noun = find_noun(sent)
        adjective = find_adjective(sent)
        verb = find_verb(sent)
    logger.info("Pronoun=%s, noun=%s, adjective=%s, verb=%s", pronoun, noun, adjective, verb)
    return pronoun, noun, adjective, verb


def filter_response(resp):
    """Don't allow any words to match our filter list"""
    tokenized = resp.split(' ')
    for word in tokenized:
        if '@' in word or '#' in word or '!' in word:
            raise UnacceptableUtteranceException()
        for s in FILTER_WORDS:
            if word.lower().startswith(s):
                raise UnacceptableUtteranceException()


def preprocess_text(sentence):
    """Handle some weird edge cases in parsing, like 'i' needing to be capitalized
    to be correctly identified as a pronoun"""
    cleaned = []
    words = sentence.split(' ')
    for w in words:
        if w == 'i':
            w = 'I'
        if w == "i'm":
            w = "I'm"
        cleaned.append(w)

    return ' '.join(cleaned)


# *************LEGACY CODE**************** #

# # start:example-respond.py
# def respond(sentence):
#     """Parse the user's inbound sentence and find candidate terms that make up a best-fit response"""
#     cleaned = preprocess_text(sentence)
#     parsed = TextBlob(cleaned)
#
#     # Loop through all the sentences, if more than one. This will help extract the most relevant
#     # response text even across multiple sentences (for example if there was no obvious direct noun
#     # in one sentence
#     pronoun, noun, adjective, verb = find_candidate_parts_of_speech(parsed)
#
#     # If we said something about the bot and used some kind of direct noun, construct the
#     # sentence around that, discarding the other candidates
#     resp = check_for_comment_about_bot(pronoun, noun, adjective)
#
#     # If we just greeted the bot, we'll use a return greeting
#     if not resp:
#         resp = check_for_greeting(parsed)
#
#     if not resp:
#         # If we didn't override the final sentence, try to construct a new one:
#         if not pronoun:
#             resp = random.choice(NONE_RESPONSES)
#         elif pronoun == 'I' and not verb:
#             resp = random.choice(COMMENTS_ABOUT_SELF)
#         else:
#             resp = construct_response(pronoun, noun, verb)
#
#     # If we got through all that with nothing, use a random response
#     if not resp:
#         resp = random.choice(NONE_RESPONSES)
#
#     logger.info("Returning phrase '%s'", resp)
#     # Check that we're not going to say anything obviously offensive
#     filter_response(resp)
#
#     return resp
