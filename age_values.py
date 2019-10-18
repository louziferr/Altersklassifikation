import json

# Klasse zum Berechnen der Werte von den durchschnittlichen Tweets der Altersgruppen

class AgeValues:

    def __init__(self, wordfile, specialfile):
        file = open(wordfile, "r")
        self.wordfreq = json.load(file)
        file.close()

        special = open(specialfile)
        self.specialfreq = json.load(special)
        special.close()

        self.ages = {"16": -14, "18": -12, "20": -10, "25": -5, "30": 0, "35": 5, "40": 10, "45": 15, "50": 20}

        self.values = dict() # Dict mit den Werten der einzelnen Token

        self.special_values = dict() # Dict mit den Werten der Worte (negativ=jung, positiv=alt)

    # Funktion, um die Frequenz eines Wortes bei einem bestimmten Alter zu bekommen
    def get_freq(self, dict, word, age):
        if age in dict:
            if word in dict[age]:
                return dict[age][word]
        return 0

    # Funktion, um den Wert eines Token zu berechnen
    def calc_value(self, word, dict):
        val = 0
        i = 0
        for age in self.ages:
            freq = self.get_freq(dict, word, age)
            val += freq*self.ages[age]
            i += 1
        return val/i

    # Funktion, um die Werte aller Zeichen zu berechnen
    def calc_all_values(self, kind):
        if kind == "words":
            for age in self.wordfreq:
                for word in self.wordfreq[age]:
                    self.values[word] = self.calc_value(word, self.wordfreq)
        elif kind == "special":
            for age in self.specialfreq:
                for thing in self.specialfreq[age]:
                    self.special_values[thing] = self.calc_value(thing, self.specialfreq)

    def save_as_json(self, dict, name):
        file_des = open(name, "w")

        # dump tweets to the file
        json.dump(dict, file_des, indent=4, sort_keys=True)

        # close the file_des
        file_des.close()


if __name__ == "__main__":
    test = AgeValues("Modelle/word_freq.json", "Modelle/special_freq.json")

    def compare(word):
        print(test.get_freq(test.wordfreq, word, "16"))
        print(test.get_freq(test.wordfreq, word, "18"))
        print(test.get_freq(test.wordfreq, word, "20"))
        print(test.get_freq(test.wordfreq, word, "25"))
        print(test.get_freq(test.wordfreq, word, "30"))
        print(test.get_freq(test.wordfreq, word, "35"))
        print(test.get_freq(test.wordfreq, word, "40"))
        print(test.get_freq(test.wordfreq, word, "45"))
        print(test.get_freq(test.wordfreq, word, "50"))

    compare("sicherheit")

    test.calc_all_values("words")

    file = open("wortwerte.txt", "w")

    for key, value in sorted(test.values.items(), key=lambda item: item[1]):
        if value != 0.0:
            file.write(str(key) + "\t" + str(value) + "\n")

    file.close()

    #test.calc_all_values("special")
#
    #file = open("spezialwerte.json", "w")
#
    #for key, value in sorted(test.special_values.items(), key=lambda item: item[1]):
    #    file.write(str(key) + "\t" + str(value) + "\n")
#
    #file.close()




