import json
from nltk.tokenize import TweetTokenizer
import numpy
import os

# Klasse zum Berechnen der Features aller Tweets aller Altersgruppen

class AgeTraining:

    def __init__(self):
        self.words = dict() # Dict mit der Anzahl der Wörter
        self.word_freq = dict()  # Dict mit den Frequenzen der Wörter
        self.special = dict()   # Dict mit der Anzahl an Sondersachen (Retweets, Mentions, Hashtags, Links)
        self.special_freq = dict()  # Dict mit der Frequenz der Sondersachen


    # Funktion, um alle json-Dateien in einem Ordner zu lesen, um das Modell zu trainieren
    def train_age(self, directory, age):

        # Dict mit dem zugehörigen Alter initiieren
        self.words[age] = dict()
        self.words[age]["total"] = 0
        # Dict mit Features vorbereiten
        self.build_special_dict(age)

        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                print(str(age) + " " + filename)
                # Alle Tweets eines Users klassifizieren
                self.train_user(directory + "/" + filename, age)

        # Frequenzen der Wörter berechnen
        self.calc_freq(age)

        # Frequenzen der Sondersachen zu berechnen
        self.calc_special_freq(age)

    def build_special_dict(self, age):
        self.special[age] = dict()
        self.special[age]["RETWEETS"] = 0
        self.special[age]["MENTIONS"] = 0
        self.special[age]["HASHTAGS"] = 0
        self.special[age]["LINKS"] = 0
        self.special[age]["TWEETS"] = 0
        # self.special[age]["LENGTHENING"] = 0
        self.special[age]["WORDLENGTH"] = 0
        self.special[age]["TWEETLENGTH"] = 0
        self.special[age]["CAPITALIZED"] = 0
        self.special[age]["COMMA"] = 0

    # Funktion zählt die Wörter aller Tweets eines Users
    def train_user(self, userfile, age):
        # Datei öffnen
        with open(userfile, 'r') as f:
            user = json.loads(f.read())

        # über alle Tweets iterieren
        for tweet in user:

            # Tweet zählen
            self.special[age]["TWEETS"] += 1

            text = user[tweet]["text"][2:-1]

            # Text richtig kodieren
            text = text.encode().decode('unicode-escape').encode("latin").decode("utf8")

            # Checken, ob es ein Retweet ist
            if text[0:2] == "RT":
                self.special[age]["RETWEETS"] += 1
            else:
                self.train_tweet(text, age)

    # Funktion, um den Tweet eines Users zu trainieren
    def train_tweet(self, text, age):
        # Tokenisierer
        tknzr = TweetTokenizer()
        # jedes Wort zählen
        for word in tknzr.tokenize(text):
            # checken, ob das Wort gesondert behandelt werden muss
            if not self.is_special(word, age):
                # checken, ob es CAPITALIZED ist
                if word == word.upper():
                    self.special[age]["CAPITALIZED"] += 1
                # normale Wörter
                word = word.lower()  # Wort in Kleinbuchstaben
                if word not in self.words[age]:
                    self.words[age][word] = 0
                # Wort kommt einmal vor: in wordcount festhalten
                self.words[age][word] += 1

                # Länge des Wortes festhalten
                self.special[age]["WORDLENGTH"] += len(word)

                # Gesamtanzahl der Wörter zählen
                self.words[age]["total"] += 1

            # Länge des Tweets festhalten
            self.special[age]["TWEETLENGTH"] += 1


    # checkt, ob ein Wort ein Hashtag, Link oder eine Mention ist
    def is_special(self, word, age):
        # Mentions
        if word[0] == "@":
            self.special[age]["MENTIONS"] += 1
            return True
        # Hashtags
        if word[0] == "#":
            self.special[age]["HASHTAGS"] += 1
            return True
        # Links
        if word[:4] == "http":
            self.special[age]["LINKS"] += 1
            return True
        if word == ",":
            self.special[age]["COMMA"] += 1
            return True
        return False

    # Funktion, um die Frequenz der Wörter zu berechnen
    def calc_freq(self, age):
        self.word_freq[age] = dict()
        if len(self.words) > 0:
            # momentanes dict, in dem die Anzahl der Wörter nachgeguckt wird
            wordcount = self.words[age]
            for word in wordcount:
                # Anzahl der Vorkommen des momentanen Wortes
                self.word_freq[age][word] = numpy.log(wordcount[word] + 0.1 /
                                                      wordcount["total"] * 1.01)

    # Funktion, um auf das Alters-dict zuzugreifen
    def get_freq(self, age, word):
        if age in self.word_freq:
            if word in self.word_freq[age]:
                return self.word_freq[age][word]
        return 0

    ######################### SONDERSACHEN ##################################

    # Funktion, um die Frequenzen der Sonderzeichen zu berechnen
    def calc_special_freq(self, age):
        self.special_freq[age] = dict()
        if len(self.special) > 0:
            # momentanes Dict mit Sondersachen
            special = self.special[age]

            # Sondersachen, deren Frequenz mit der Gesamtanzahl der Wörter berechnet werden
            word_specials = ["MENTIONS", "HASHTAGS", "WORDLENGTH", "CAPITALIZED"]
            for thing in word_specials:
                self.special_freq[age][thing] = special[thing] / self.words[age]["total"]

            # Sondersachen, deren Frequenz mit der Gesamtanzahl der Tweets berechnet werden
            tweet_specials = ["RETWEETS", "LINKS", "TWEETLENGTH"]

            for thing in tweet_specials:
                self.special_freq[age][thing] = special[thing] / self.special[age]["TWEETS"]

    # Zugriff auf die Frequenz der Sondersachen
    def get_special_freq(self, age, word):
        if age in self.special_freq:
            if word in self.special_freq[age]:
                return self.special_freq[age][word]
        return 0

    def split_80_20(self, json_file):
        with open(json_file, 'r') as f:
            user = json.loads(f.read())

        test = dict()
        train = dict()

        i = 0
        x = 0
        y = 0

        for tweet in user:
            if i%5 == 0:
                test[x] = user[tweet]
                x += 1
            else:
                train[y] = user[tweet]
                y += 1
            i += 1

        self.save_as_json(test, json_file[:-5] + "_test.json")
        self.save_as_json(train, json_file[:-5] + "_train.json")

    def split_all(self, directory):
        for subdir, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".json"):
                    print(os.path.join(subdir, file))
                    # Alle Tweets eines Users klassifizieren
                    self.split_80_20(os.path.join(subdir, file))

    # Dict als json-Datei speichern
    def save_as_json(self, dict, name):
        file_des = open(name, "w", encoding="utf8")

        # dump tweets to the file
        json.dump(dict, file_des, indent=4, sort_keys=True)

        print("Dict saved as " + name)

        # close the file_des
        file_des.close()


if __name__ == "__main__":
    test = AgeTraining()
    test.train_age("TweetCollecting/Trainset/16", 16)
    test.train_age("TweetCollecting/Trainset/18", 18)
    test.train_age("TweetCollecting/Trainset/20", 20)
    test.train_age("TweetCollecting/Trainset/25", 25)
    test.train_age("TweetCollecting/Trainset/30", 30)
    test.train_age("TweetCollecting/Trainset/35", 35)
    test.train_age("TweetCollecting/Trainset/40", 40)
    test.train_age("TweetCollecting/Trainset/45", 45)
    test.train_age("TweetCollecting/Trainset/50", 50)

    #test.test.calc_special_val()
    #test.calc_all_age_values()

    #print(test.word_values["xd"])

    test.save_as_json(test.word_freq, "word_freq.json")
    #test.save_as_json(test.special_freq, "special_freq.json")
