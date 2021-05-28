import pickle
from tqdm import tqdm
from docopt import docopt


def main():
    args = docopt("""Read a data set and save pairs as set of tuples (noun1 n, noun2 n), duplicates and autohypernyms are excluded
    
    Usage:
        read_dataset.py <input_file_dataset> (-g | -n | -w) <output_file_dataset> | <input_file_dataset> <input_file_dataset2> -e <output_file_dataset>
        
    Arguments:
        <input_file_dataset> = file containing the data set (.txt)
        <input_file_dataset2> = file containing the data set (.txt), for english standard separated into test + val
        <output_file_dataset> = file to save the pickled data set
        
    Options:
        -g --germanet  read GermaNet
        -n --ghostnn  read GhostNN
        -e --english  read english standard data set (e.g. BLESS, EVALution, Lenci/Benotto, Weeds)
        -w --wordnet  read WordNet
    
    """)

    # get arguments amd options
    input_file_dataset = args['<input_file_dataset>']
    input_file_dataset2 = args['<input_file_dataset2>']
    output_file_dataset = args['<output_file_dataset>']
    is_germanet = args['--germanet']
    is_ghostnn = args['--ghostnn']
    is_english = args['--english']
    is_wordnet = args['--wordnet']

    if is_germanet:
        print("Reading data set...")
        dataset = readGermaNet(input_file_dataset)
        print("Number of noun-noun pairs: " + str(len(dataset)))
        save_to_pickle(dataset, output_file_dataset)
        print("Data set saved")
    if is_ghostnn:
        print("Reading data set...")
        dataset = readGhostNN(input_file_dataset)
        print("Number of noun-noun pairs: " + str(len(dataset)))
        print(len(dataset))
        save_to_pickle(dataset, output_file_dataset)
        print("Data set saved")
    if is_english:
        print("Reading data set...")
        dataset = read_englishStandard(input_file_dataset, input_file_dataset2)
        print("Number of noun-noun pairs: " + str(len(dataset)))
        print(len(dataset))
        save_to_pickle(dataset, output_file_dataset)
        print("Data set saved")
    if is_wordnet:
        print("Reading data set...")
        dataset = read_wordNet(input_file_dataset)
        print("Number of noun-noun pairs: " + str(len(dataset)))
        print(len(dataset))
        save_to_pickle(dataset, output_file_dataset)
        print("Data set saved")


def readGermaNet(germaNet: str):
    """
    this function reads the germaNet data set and stores it in a set, which contains tuples of the word pairs
    :param germaNet: the germaNet file
    :return: set of word pairs
    """
    wordPairsGermaNet = set()

    with open(germaNet) as germaNet:
        for line in germaNet:
            line = line.strip()
            line = line.split("\t")
            # filter out auto-hypernyms
            if line[4] != line[6]:
                hypo = line[4] + " " + "n"
                hyper = line[6] + " " + "n"
                wordPairsGermaNet.add((hypo, hyper))

    return wordPairsGermaNet


def readGhostNN(ghostNN: str):
    """
    this function reads the ghostNN data set and stores it in a set, which contains tuples of the word pairs
    :param ghostNN: the ghostNN file
    :return: set of word pairs
    """
    wordPairsGhostNN = set()

    with open(ghostNN) as ghostNN:
        # skip header line
        next(ghostNN)
        for line in ghostNN:
            line = line.strip()
            line = line.split("\t")
            hypo = line[0] + " " + "n"
            hyper = line[2] + " " + "n"
            wordPairsGhostNN.add((hypo, hyper))

    return wordPairsGhostNN


def read_englishStandard(englishStandardTest: str, englishStandardVal: str):
    """
    read an english standart data set consisting of two parts, test and val (e.g. BLESS, EVALution, Lenci/Benotto, Weeds)
    :param englishStandardTest: the test set
    :param englishStandardVal: the validation set
    :return: set of word pairs
    """
    wordPairsEnglish = set()

    with open(englishStandardTest) as englishStandardTest:
        for line in englishStandardTest:
            line = line.strip()
            line = line.split("\t")
            # only include hypernymy related pairs
            if line[3] == "hyper" and line[2] == "True":
                hypo = line[0].split("-")
                hyper = line[1].split("-")
                # only include nouns
                if hypo[1] == "n" and hyper[1] == "n":
                    hypo = hypo[0] + " " + "n"
                    hyper = hyper[0] + " " + "n"
                    wordPairsEnglish.add((hypo, hyper))

    # same as above for the validation set
    with open(englishStandardVal) as englishStandardVal:
        for line in englishStandardVal:
            line = line.strip()
            line = line.split("\t")
            if line[3] == "hyper" and line[2] == "True":
                hypo = line[0].split("-")
                hyper = line[1].split("-")
                if hypo[1] == "n" and hyper[1] == "n":
                    hypo = hypo[0] + " " + "n"
                    hyper = hyper[0] + " " + "n"
                    wordPairsEnglish.add((hypo, hyper))

    return wordPairsEnglish


def read_wordNet(wordNet: str):
    """
    read the wordNet data set
    :param wordNet: the wordNet file
    :return: set of word pairs
    """
    wordPairsWordNet = set()

    with open(wordNet) as wordNet:
        for line in wordNet:
            line = line.strip()
            line = line.split("\t")
            # only include nouns with hypernyms
            if len(line) > 1:
                hypo = line[0]
                hyperList = line[1]
                hyperList = hyperList.split(",")
                for hyper in hyperList:
                    # exclude auto-hypernyms
                    if hypo != hyper:
                        hypoLemma = hypo + " " + "n"
                        hyperLemma = hyper + " " + "n"
                        wordPairsWordNet.add((hypoLemma, hyperLemma))

    return wordPairsWordNet


def read_from_pickle(file: str):
    """
    this function reads an object from a pickle file and returns it
    :param file: the file containing the object
    :return obj: the object
    """
    obj = pickle.load(open(file, "rb"))
    return obj


def save_to_pickle(obj, file: str):
    """
    this function saves an object to a pickle file
    :param obj: the object
    :param file: the file to save the object
    """
    pickle.dump(obj, open(file, "wb"), protocol=4)


if __name__ == '__main__':
    main()
