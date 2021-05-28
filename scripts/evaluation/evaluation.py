import pickle
from tabulate import tabulate
from tqdm import tqdm
from docopt import docopt

def main():
    args = docopt("""Evaluate measure(s) on data set(s) and save results in .txt file(s)
    
    Usage:
        evaluation.py (-f <results_freq> | -l | -w <results_weedsPrec> | -i <results_invCL> | -r <results_slqsRow> | -s <results_slqs>)... (-a <output_file_accuracy> | -c <output_file_smc> | -p <output_file_proportions>)... (<dataset_file> <name>)...
        
    Arguments:
        <results_freq> = pickled word frequency results
        <results_weedsPrec> = pickled weedsPrec results
        <results_invCL> = pickled invCL results
        <results_slqsRow> = pickled SLQS Row results
        <results_slqs> = pickled SLQS results
        <output_file_accuracy> = file to save accuracy (.txt)
        <output_file_smc> = file to save SMC (.txt)
        <output_file_proportions> = file to save intersection proprtions (.txt), table format: p1|p2
        <dataset_file> = pickled data set
        <name> = name of the data set
        
    Options:
        -f --frequency  evaluate word frequency
        -l --length  evaluate word length
        -w --weedsprec  evaluate weedsPrec
        -i --invcl  evaluate invCL
        -r --row  evaluate slqs row
        -s --slqs  evaluate slqs
        -a --accuracy  calculate accuracy
        -c --correlation  claculate smc correlations
        -p --proportions  calculate intersection proportions
    
    """)

    #get arguments and options
    results_freq = args['<results_freq>']
    results_weedsPrec = args['<results_weedsPrec>']
    results_invCL = args['<results_invCL>']
    results_slqsRow = args['<results_slqsRow>']
    results_slqs = args['<results_slqs>']

    output_file_accuracy = args['<output_file_accuracy>']
    output_file_smc = args['<output_file_smc>']
    output_file_proportions = args['<output_file_proportions>']

    dataset_file = args['<dataset_file>']
    name = args['<name>']

    is_frequency = args['--frequency']
    is_length = args['--length']
    is_weedsprec = args['--weedsprec']
    is_invcl = args['--invcl']
    is_row = args['--row']
    is_slqs = args['--slqs']

    is_accuracy = args['--accuracy']
    is_correlation = args['--correlation']
    is_proportions = args['--proportions']

    print("Loading data sets...")
    datasets = []
    for data in dataset_file:
        dataset = list(read_from_pickle(data))
        datasets.append(dataset)
    names = []
    for n in name:
        nam = str(n)
        names.append(nam)
    print("Loaded data sets")

    measures = []
    if is_frequency:
        measures.append("frequency")
    if is_length:
        measures.append("wordLength")
    if is_weedsprec:
        measures.append("weedsPrec")
    if is_invcl:
        measures.append("invCL")
    if is_row:
        measures.append("slqsRow")
    if is_slqs:
        measures.append("slqs")

    evaluation = Evaluation(is_frequency, is_length, is_weedsprec, is_invcl, is_row, is_slqs, results_freq, results_weedsPrec, results_invCL, results_slqsRow, results_slqs)

    if is_accuracy:
        print("Calculating accuracy...")
        with open(output_file_accuracy[0], "w+") as accuracyFile:
            table = []
            for measure in tqdm(measures):
                line = []
                line.append(measure)
                for dataset in datasets:
                    ev = evaluation.get_evaluation(measure, dataset)
                    acc = ev[0]
                    acc = round(acc, 4)

                    line.append(acc)
                table.append(line)
            accuracyFile.write(tabulate(table, headers=names, tablefmt="plain"))
        print("Calculated accuracy")

    if is_correlation:
        print("Calculating SMC correlations...")
        with open(output_file_smc[0], "w+") as smcFile:
            for dataset in tqdm(datasets):
                i = datasets.index(dataset)
                smcFile.write(names[i] + "\n")
                table = []
                for measure1 in measures:
                    line = []
                    line.append(measure1)
                    for measure2 in measures:
                        ev1 = evaluation.get_evaluation(measure1, dataset)
                        ev2 = evaluation.get_evaluation(measure2, dataset)
                        smc = evaluation.smc(ev1[3], ev2[3])
                        smc = round(smc, 3)

                        line.append(smc)
                    table.append(line)
                smcFile.write(tabulate(table, headers=measures, tablefmt="plain"))
                smcFile.write("\n\n")
        print("Calculated SMC correlations")

    if is_proportions:
        print("Calculating intersection proportions...")
        with open(output_file_proportions[0], "w+") as propFile:
            for dataset in tqdm(datasets):
                i = datasets.index(dataset)
                propFile.write(names[i] + "\n")
                table = []
                for measure1 in measures:
                    line = []
                    line.append(measure1)
                    for measure2 in measures:
                        ev1 = evaluation.get_evaluation(measure1, dataset)
                        ev2 = evaluation.get_evaluation(measure2, dataset)
                        proportions = evaluation.intersections(ev1, ev2)
                        proportion1 = round(proportions[0], 3)
                        proportion2 = round(proportions[1], 3)

                        line.append(str(proportion1) + "|" + str(proportion2))
                    table.append(line)
                propFile.write(tabulate(table, headers=measures, tablefmt="plain"))
                propFile.write("\n\n")
        print("Calculated intersection proportions")


def accuracy(evaluation):
    """
    Calculate accuracy
    :param evaluation: input
    :return: accuracy
    """
    accuracy = evaluation[0] / (evaluation[0]+evaluation[1])

    checkSum = evaluation[0] + evaluation[1]
    #print(checkSum)

    return accuracy

def evaluate_weedsPrec_invCL(results: dict, wordPairs: list):
    """
    Evaluate Weeds Precision or InvCL
    :param results: WeedsPrec/InvCL results
    :param wordPairs: the word pairs
    :return: evaluation
    """
    correct = 0
    incorrect = 0
    correctDict = {}
    incorrectDict = {}
    vector = []

    # iterate over word pairs
    for wordPair in wordPairs:
        hypo = wordPair[0]
        hyper = wordPair[1]

        # WeedsPrec should be higher for (hypo, hyper)
        if results[(hypo,hyper)] > results[(hyper,hypo)]:
            correct += 1
            vector.append(1)
            correctDict[wordPair] = [results[(hypo,hyper)], results[(hyper,hypo)]]
        else:
            incorrect += 1
            vector.append(0)
            incorrectDict[(hypo,hyper)] = [results[(hypo,hyper)], results[(hyper,hypo)]]

    return correct,incorrect, correctDict, incorrectDict, vector

def evaluate_slqs(results:dict, wordPairs:list):
    """
    Evaluate SLQS
    :param results: SLQS results
    :param wordPairs: the word pairs
    :return: evaluation
    """
    correct = 0
    incorrect = 0
    correctDict = {}
    incorrectDict = {}
    vector = []

    # iterate over word pairs
    for wordPair in wordPairs:
        slqs = results[wordPair]
        # slqs should be >0 for a pair
        if slqs > 0:
            correct += 1
            vector.append(1)
            correctDict[wordPair] = slqs
        else:
            incorrect += 1
            vector.append(0)
            incorrectDict[wordPair] = slqs

    return correct, incorrect, correctDict, incorrectDict, vector

def evaluate_frequency(wordFrequency:dict, wordPairs:list):
    """
    Evaluate word frequency
    :param wordFrequency: results word frequency
    :param wordPairs: the word pairs
    :return: evaluation
    """
    correct = 0
    incorrect = 0
    correctDict = {}
    incorrectDict = {}
    vector = []

    # iterate over word pairs
    for wordPair in wordPairs:
        hypo = wordPair[0]
        hyper = wordPair[1]

        # word frequency of hyper should be higher than word frequency of hypo
        if wordFrequency[hyper] > wordFrequency[hypo]:
            correct += 1
            vector.append(1)
            correctDict[wordPair] = [wordFrequency[hypo], wordFrequency[hyper]]
        else:
            incorrect += 1
            vector.append(0)
            incorrectDict[wordPair] = [wordFrequency[hypo], wordFrequency[hyper]]

    return correct,incorrect, correctDict, incorrectDict, vector

def evaluate_wordLength(wordPairs:list):
    """
    Evaluate word length
    :param wordPairs: the word pairs
    :return: evaluation
    """
    correct = 0
    incorrect = 0
    correctDict = {}
    incorrectDict = {}
    vector = []

    # iterate over word pairs
    for pair in wordPairs:
        # get rid of pos-tag
        hypo = pair[0]
        hypo = hypo.split(" ")
        hypo = hypo[0]
        hyper = pair[1]
        hyper = hyper.split(" ")
        hyper = hyper[0]

        # word length of hypo should be higher than word length of hyper
        if len(hypo) > len(hyper):
            correct += 1
            vector.append(1)
            correctDict[pair] = [len(hypo), len(hyper)]
        else:
            incorrect += 1
            vector.append(0)
            incorrectDict[pair] = [len(hypo), len(hyper)]

    return correct,incorrect, correctDict, incorrectDict, vector


class Evaluation:

    def __init__(self, is_frequency, is_length, is_weedsprec, is_invcl, is_row, is_slqs, results_freq, results_weedsPrec, results_invCL, results_slqsRow, results_slqs):
        """
        
        :param is_frequency: 
        :param is_length: 
        :param is_weedsprec: 
        :param is_invcl: 
        :param is_row: 
        :param is_slqs: 
        :param results_freq: 
        :param results_weedsPrec: 
        :param results_invCL: 
        :param results_slqsRow: 
        :param results_slqs: 
        """
        print("Loading results...")
        if is_frequency:
            self.resultsFrequency = read_from_pickle(results_freq[0])
        if is_weedsprec:
            self.resultsWeedsPrec = read_from_pickle(results_weedsPrec[0])
        if is_invcl:
            self.resultsInvCL = read_from_pickle(results_invCL[0])
        if is_row:
            self.resultsSLQSRow = read_from_pickle(results_slqsRow[0])
        if is_slqs:
            self.resultsSLQS = read_from_pickle(results_slqs[0])
        print("Loaded results")


    def weedsPrec(self, pairs:list):
        """
        WeedsPrec
        :param pairs: the word pairs
        :return: evaluation
        """
        evaluation = evaluate_weedsPrec_invCL(self.resultsWeedsPrec, pairs)
        acc = accuracy(evaluation)
        correct = evaluation[0]
        incorrect = evaluation[1]
        vector = evaluation[4]
        correctDict = evaluation[2]
        incorrectDict = evaluation[3]

        return acc, correct, incorrect, vector, correctDict, incorrectDict

    def invCL(self, pairs: list):
        """
        InvCL
        :param pairs: the word pairs
        :return: evaluation
        """
        evaluation = evaluate_weedsPrec_invCL(self.resultsInvCL, pairs)
        acc = accuracy(evaluation)
        correct = evaluation[0]
        incorrect = evaluation[1]
        vector = evaluation[4]
        correctDict = evaluation[2]
        incorrectDict = evaluation[3]

        return acc, correct, incorrect, vector, correctDict, incorrectDict

    def slqs(self, pairs: list):
        """
        SLQS
        :param pairs: the word pairs
        :return: evaluation
        """
        evaluation = evaluate_slqs(self.resultsSLQS, pairs)
        acc = accuracy(evaluation)
        correct = evaluation[0]
        incorrect = evaluation[1]
        vector = evaluation[4]
        correctDict = evaluation[2]
        incorrectDict = evaluation[3]

        return acc, correct, incorrect, vector, correctDict, incorrectDict

    def slqsRow(self, pairs: list):
        """
        SLQS Row
        :param pairs: the word pairs
        :return: evaluation
        """
        evaluation = evaluate_slqs(self.resultsSLQSRow, pairs)
        acc = accuracy(evaluation)
        correct = evaluation[0]
        incorrect = evaluation[1]
        vector = evaluation[4]
        correctDict = evaluation[2]
        incorrectDict = evaluation[3]

        return acc, correct, incorrect, vector, correctDict, incorrectDict

    def frequency(self, pairs: list):
        """
        word frequency
        :param pairs: the word pairs
        :return: evaluation
        """
        evaluation = evaluate_frequency(self.resultsFrequency, pairs)
        acc = accuracy(evaluation)
        correct = evaluation[0]
        incorrect = evaluation[1]
        vector = evaluation[4]
        correctDict = evaluation[2]
        incorrectDict = evaluation[3]

        return acc, correct, incorrect, vector, correctDict, incorrectDict

    def wordLength(self, pairs:list):
        """
        word length
        :param pairs: the word pairs
        :return: evaluation
        """
        evaluation = evaluate_wordLength(pairs)
        acc = accuracy(evaluation)
        correct = evaluation[0]
        incorrect = evaluation[1]
        vector = evaluation[4]
        correctDict = evaluation[2]
        incorrectDict = evaluation[3]

        return acc, correct, incorrect, vector, correctDict, incorrectDict

    def smc(self, vector1:list, vector2:list):
        """
        Calculate SMC correlation as described in:
        Robert R. Sokal. A statistical method for evaluating systematic relationships. Univ. Kansas, Sci. Bull. 1958
        :param vector1: vector of measure 1
        :param vector2: vector of measure 2
        :return: SMC correlation
        """
        # check if vectors have equal length
        if len(vector1) != len(vector2):
            print("Error")

        # count matching predictions
        numerator = 0
        for i in range(len(vector1)):
            if vector1[i] == vector2[i]:
                numerator += 1

        # calculate SMC
        smc = numerator/len(vector1)
        return smc

    def intersections(self, evaluation1, evaluation2):
        """
        Calculate intersection proportions
        :param evaluation1: evaluation of measure 1
        :param evaluation2: evaluation of measure 2
        :return: intersections and proportions
        """
        correct1 = set(evaluation1[4].keys())
        incorrect2 = set(evaluation2[5].keys())

        # get intersect
        intersect = correct1 & incorrect2

        # get proportions p1 and p2
        if len(correct1) > 0:
            proportion1 = len(intersect) / len(correct1)
        else:
            proportion1 = 0
        if len(incorrect2) > 0:
            proportion2 = len(intersect) / len(incorrect2)
        else:
            proportion2 = 0

        return proportion1, proportion2, intersect

    def get_evaluation(self, measure:str, pairs:list):
        """
        Get evaluation for measure
        :param measure: the measure
        :param pairs: the word pairs
        :return: evaluation
        """
        evaluation = 20

        if measure == "weedsPrec":
            evaluation = self.weedsPrec(pairs)
        if measure == "invCL":
            evaluation = self.invCL(pairs)
        if measure == "slqs":
            evaluation = self.slqs(pairs)
        if measure == "slqsRow":
            evaluation = self.slqsRow(pairs)
        if measure == "frequency":
            evaluation = self.frequency(pairs)
        if measure == "wordLength":
            evaluation = self.wordLength(pairs)

        if evaluation == 20:
            print("Error")

        return evaluation

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