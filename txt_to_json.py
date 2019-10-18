import json

if __name__ == "__main__":
    file = "Modelle/wortwerte.txt"

    textfile = open(file, "r", encoding="utf8")

    jsonfile = open(file[:-4] + ".json", "w", encoding="utf8")

    dicc = dict()

    for line in textfile:
        splitted = line.strip("\n").split("\t")

        if len(splitted) == 2:
            dicc[splitted[0]] = splitted[1]

    json.dump(dicc, jsonfile, indent=4, sort_keys=True)

    textfile.close()

    jsonfile.close()
