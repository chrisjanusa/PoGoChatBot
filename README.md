# PoGoChatBot

Must pip install following libraries:
- pandas
- bs4
- requests
- textblob
- spacy
- python-Levenshtein

Must also run:

    python -m spacy download en
Or maybe:

    python3 -m spacy download en

In order to run pogo you must first run Gather_All_Info.py in order to scrape the needed information off the internet.
Then you can run ChatBot.py and begin conversing with Pogo.

It will prompt you for your name which is needed to create a profile then after it is given a name, Pogo will prompt you with example questions.
We recommend using the show all command to get full list of phrases that can be used.
These phrases need not be word for word but must be on same topic to match what Pogo has knowledge of.

When you are done conversing tell Pogo 'bye' so it knows to exit and save your user profile
