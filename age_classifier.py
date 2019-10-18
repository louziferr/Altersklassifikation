import json
from nltk.tokenize import TweetTokenizer
import os

# Klasse zum Klassifizieren des Alters von Twitter-Usern

class AgeClassifier:
    def __init__(self, word_values_file, special_values_file):
        wordvalues = open(word_values_file, "r", encoding="utf8")
        self.word_values = json.load(wordvalues)
        wordvalues.close()

        special = open(special_values_file, "r", encoding="utf8")
        self.specialvalues = json.load(special)
        special.close()

        # dict mit den Maximum-Werten zu den Altersgruppen
        self.age_classifier = {0: 16, 2: 18, 2.5: 20, 3.0: 25, 3.3: 30, 3.5: 35, 4.0: 40, 4.5: 45}

        # Alle Altersgruppen und wie viele User dieser richtig bzw. falsch zugeordnet wurden
        self.classified_ages = {16: {"r": 0, "f": {18: 0, 20: 0, 25: 0, 30: 0, 35: 0, 40: 0, 45: 0, 50: 0}, "false": 0},
                                18: {"r": 0, "f": {16: 0, 20: 0, 25: 0, 30: 0, 35: 0, 40: 0, 45: 0, 50: 0}, "false": 0},
                                20: {"r": 0, "f": {16: 0, 18: 0, 25: 0, 30: 0, 35: 0, 40: 0, 45: 0, 50: 0}, "false": 0},
                                25: {"r": 0, "f": {16: 0, 18: 0, 20: 0, 30: 0, 35: 0, 40: 0, 45: 0, 50: 0}, "false": 0},
                                30: {"r": 0, "f": {16: 0, 18: 0, 20: 0, 25: 0, 35: 0, 40: 0, 45: 0, 50: 0}, "false": 0},
                                35: {"r": 0, "f": {16: 0, 18: 0, 20: 0, 25: 0, 30: 0, 40: 0, 45: 0, 50: 0}, "false": 0},
                                40: {"r": 0, "f": {16: 0, 18: 0, 20: 0, 25: 0, 30: 0, 35: 0, 45: 0, 50: 0}, "false": 0},
                                45: {"r": 0, "f": {16: 0, 18: 0, 20: 0, 25: 0, 30: 0, 35: 0, 40: 0, 50: 0}, "false": 0},
                                50: {"r": 0, "f": {16: 0, 18: 0, 20: 0, 25: 0, 30: 0, 35: 0, 40: 0, 45: 0}, "false": 0}}

    # Berechnen des Wertes zu einem Tweet
    def calc_value(self, tweet_text):
        val = 0
        words = 0
        # Tokenisierer
        tknzr = TweetTokenizer()
        # jedes Wort zählen
        for word in tknzr.tokenize(tweet_text):
            val += self.check_special(word)
            words += 1
            word = word.lower()
            val += self.get_value(word)
        return val/words

    # Überprüfen, ob ein Wort ein besonderes Feature hat
    def check_special(self, word):
        if (word.upper() == word):
            # Wort ist in Großbuchstaben geschrieben
            return self.specialvalues["CAPITALIZED"]
        if (word[0] == "#"):
            # Wort ist ein Hashtag
            return self.specialvalues["HASHTAGS"]
        if (word[0] == "@"):
            # Wort ist eine Mention
            return self.specialvalues["MENTIONS"]
        if word[:4] == "http":
            # Wort ist ein Link
            return self.specialvalues["LINKS"]
        return 0

    # Getter für den Wert eines Wortes aus einem Tweet
    def get_value(self, word):
        if word in self.word_values:
            return self.word_values[word]
        else:
            return 0

    # Tweet klassifizieren
    def classify_tweet(self, tweet_text):
        value = self.calc_value(tweet_text)
        for val in self.age_classifier:
            if value <= val:
                return self.age_classifier[val]
        return 50

    # Klassifizierung testen (alle User)
    def test_on_all(self, directory):
        tweets = 0
        right = 0
        for subdirs, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".json"):
                    print(os.path.join(subdirs, file))
                    t, r = self.test_classification(os.path.join(subdirs, file), int(subdirs[-2:]))
                    tweets += t
                    right += r
        print(tweets)
        print(right)

    # Klassifizierung testen (ein User)
    def test_classification(self, userfile, actual_age):

        file = open(userfile, "r", encoding="utf8")
        tweets = json.load(file)
        file.close()

        total_tweets = 0
        total_right = 0
        total_wrong = 0

        classified_ages = {16: 0, 18: 0, 20: 0, 25: 0, 30: 0, 35: 0, 40: 0, 45: 0, 50: 0}

        for tweet in tweets:
            total_tweets += 1
            age = test.classify_tweet(tweets[tweet]["text"][2:-1])
            classified_ages[age] += 1

        for age in classified_ages:
            if age == actual_age:
                self.classified_ages[age]["r"] += classified_ages[age]
                total_right += classified_ages[age]
            else:
                self.classified_ages[age]["false"] += classified_ages[age]
                self.classified_ages[actual_age]["f"][age] += classified_ages[age]

        return total_tweets, total_right


    # Einen User klassifizieren
    def classify_user(self, userfile):
        file = open(userfile, "r", encoding="utf8")
        user = json.load(file)
        file.close()

        classified = {16: 0, 18: 0, 20: 0, 25: 0, 30: 0, 35: 0, 40: 0, 45: 0, 50: 0}

        for tweet in user:
            guessed_age = self.classify_tweet(user[tweet]["text"][2:-1])
            classified[guessed_age] += 1
        max = self.get_max(classified)

        return max

    # maximum aus einem dictionary bekommen
    def get_max(self, dictionary):
        max = 0
        guessed_age = 0
        for age in dictionary:
            if dictionary[age] > max:
                max = dictionary[age]
                guessed_age = age
        return guessed_age

    # dict als json-Datei speichern
    def save_as_json(self, dict, name):
        file_des = open(name, "w")

        # dump tweets to the file
        json.dump(dict, file_des, indent=4, sort_keys=True)

        # close the file_des
        file_des.close()


if __name__ == "__main__":
    test = AgeClassifier("Modelle/wortwerte.json", "Modelle/spezialwerte.json")

    ages = dict()

    list_ages = ["16", "18", "20", "25", "30", "35", "40", "45", "50"]

    items_ages = ["total_value", "tweets", "value", "min", "max"]

    for age in list_ages:
        ages[age] = dict()
        for item in items_ages:
            ages[age][item] = 0

    def train_user(file, age):
        with open(file, 'r') as f:
            user = json.loads(f.read())

        for tweet in user:
            ages[age]["tweets"] += 1
            text = user[tweet]["text"][2:-1]
            value = test.calc_value(text)
            ages[age]["total_value"] += value
            if value < ages[age]["min"]:
                ages[age]["min"] = value
            elif value > ages[age]["max"]:
                ages[age]["max"] = value
        ages[age]["value"] = ages[age]["total_value"]/ages[age]["tweets"]


    def count_values(filename, age):
        with open(filename, "r") as f:
            user=json.loads(f.read())

        i = 0

        for tweet in user:
            if i < 50:
                text = user[tweet]["text"][2:-1]
                value = test.calc_value(text)
                ages[age] += " " + str(value)
            i += 1

    #for subdirs, dirs, files in os.walk("TweetCollecting/Trainset"):
    #    for file in files:
    #        if file.endswith(".json"):
    #            print(file)
    #            train_user(os.path.join(subdirs, file), subdirs[-2:])
#
    #test.save_as_json(ages, "values_alter_special.json")

    test.test_on_all("TweetCollecting/Testset")

    test.save_as_json(test.classified_ages, "class_with_special.json")
