import pickle
from tqdm import tqdm
import random
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.tree import export_graphviz
from graphviz import Source
from subprocess import call
from docopt import docopt

def main():
    args = docopt("""Cunduct unsupervised classification on a data set with Logistic Regression and Decision Tree, with word frequency, word length and slqs as input features
    Optionally draw (part of) the decision tree and save as tree.png and tree.dot
    Optionally set maximum depth for decision tree creation
    
    Usage:
        classification.py <dataset_file> <results_freq> <results_slqs> <output_file_logReg> <output_file_decTree>
        classification.py <dataset_file> <results_freq> <results_slqs> <output_file_logReg> <output_file_decTree> -m <max_depth> 
        classification.py <dataset_file> <results_freq> <results_slqs> <output_file_logReg> <output_file_decTree> -d [-l <depth>]
        classification.py <dataset_file> <results_freq> <results_slqs> <output_file_logReg> <output_file_decTree> -m <max_depth> -d [-l <depth>]
        
    Arguments:
        <dataset_file> = pickled data set
        <results_freq> = pickled word frequency results
        <results_slqs> = pickled SLQS results
        <output_file_logReg> = file to save the results of Logistic Regression (.txt)
        <output_file_decTree> = file to save the results of Decision Tree (.txt)
        <depth> = depth to which the tree should be drawn
        <max_depth> = maximum depth for the tree creation
        
    Options:
        -d --draw  draw the decision tree
        -l --limit  draw only part of the tree
        -m --max  create tree with maximum depth
    
    """)

    #get arguments and options
    dataset_file = args['<dataset_file>']
    results_freq = args['<results_freq>']
    results_slqs = args['<results_slqs>']
    output_file_logReg = args['<output_file_logReg>']
    output_file_decTree = args['<output_file_decTree>']
    is_draw = args['--draw']
    is_limit = args['--limit']
    is_max = args['--max']
    if is_limit:
        depth = int(args['<depth>'])
    else:
        depth = 0
    if is_max:
        max_depth = int(args['<max_depth>'])
    else:
        max_depth = 0

    print("Loading results and data set")
    dataset = list(read_from_pickle(dataset_file))
    wordFreq = read_from_pickle(results_freq)
    slqs = read_from_pickle(results_slqs)
    print("Loaded results and data set")

    print("Creating vectors...")
    x, y = create_vectors_invert(dataset, wordFreq, slqs)
    print("Created vectors")

    xTrain, xTest, yTrain, yTest = train_test_split(x, y, test_size=0.2, random_state=0, stratify=y)

    print("Running Logistic Regression...")
    accuracyTraining, accuracyTest, coefficients = logistic_regression(xTrain, yTrain, xTest, yTest)
    with open(output_file_logReg, "w+") as logRegFile:
        logRegFile.write("Training accuracy: " + str(accuracyTraining) + "\n")
        logRegFile.write("Test accuracy:" + str(accuracyTest) + "\n")
        logRegFile.write("Model coefficients [word frequency, word length, slqs]: " + str(coefficients))
    print("Logistic Regression done")

    print("Running Decision Tree...")
    accuracyTraining, accuracyTest, featureImportances = decision_tree(xTrain, yTrain, xTest, yTest, is_draw, is_limit, is_max, depth, max_depth)
    with open(output_file_decTree, "w+") as decTreeFile:
        decTreeFile.write("Training accuracy: " + str(accuracyTraining) + "\n")
        decTreeFile.write("Test accuracy:" + str(accuracyTest) + "\n")
        decTreeFile.write("Feature importances [word frequency, word length, slqs]: " + str(featureImportances))
    print("Decision Tree done")


def create_vectors_invert(wordPairs:list, wordFrequency:dict, slqsResults:dict):
    """
    Create input vectors for classification with word frequency difference, word length difference ans SLQS as features
    :param wordPairs: the word pairs
    :param wordFrequency: results word frequency
    :param slqsResults: results SLQS
    :return: vectors with observations and predictions
    """
    # for random inversion of pairs
    random.shuffle(wordPairs)
    x = []
    y = []
    i = 0
    count1 = 0
    count0 = 0

    # iterate over word pairs
    for wordPair in wordPairs:
        hypo = wordPair[0]
        hyper = wordPair[1]

        # inverse calculation of feature value for every second pair
        if i % 2 == 0:
            freqDiff = wordFrequency[hyper] - wordFrequency[hypo]
        else:
            freqDiff = wordFrequency[hypo] - wordFrequency[hyper]

        if i % 2 == 0:
            slqs = slqsResults[wordPair]
        else:
            slqs = slqsResults[(hyper,hypo)]

        hypo = hypo.split(" ")
        hypo = hypo[0]
        hyper = hyper.split(" ")
        hyper = hyper[0]

        if i % 2 == 0:
            lenDiff = len(hypo) - len(hyper)
        else:
            lenDiff = len(hyper) - len(hypo)

        x.append([freqDiff, lenDiff, slqs])

        if i % 2 == 0:
            y.append(1)
            count1 += 1
        # inversed pair is wrong order (hyper, hypo)
        else:
            y.append(0)
            count0 += 1

        i += 1

    x = np.array(x)
    y = np.array(y)
    return x,y

def logistic_regression(xTrain, yTrain, xTest, yTest):
    """
    Perform Logistic Regression
    :param xTrain: training data observations
    :param yTrain: training data predictions
    :param xTest: test data observations
    :param yTest: test data predictions
    :return: evaluation
    """
    # initialize model
    model = LogisticRegression(solver="liblinear", random_state=0)
    # train model
    model.fit(xTrain, yTrain)
    # get accuracy
    accuracyTraining = model.score(xTrain, yTrain)
    accuracyTest = model.score(xTest, yTest)
    # get coefficients
    coefficients = model.coef_

    return accuracyTraining, accuracyTest, coefficients

def decision_tree(xTrain, yTrain, xTest, yTest, is_draw, is_limit, is_max, depth, max_depth):
    """
    Perform decision tree classification
    :param xTrain: training data observations
    :param yTrain: training data predictions
    :param xTest: test data observations
    :param yTest: test data predictions
    :param is_draw: if to draw the tree
    :param is_limit: if to set a drawing limit
    :param is_max: if to set a creation maximum
    :param depth: the optional drawing limit
    :param max_depth: the optional maximum depth
    :return: evaluation
    """
    # check if tree should be created with maximum depth
    # initialize model
    if is_max:
        model = DecisionTreeClassifier(criterion="entropy", random_state=0, max_depth=max_depth)
    else:
        model = DecisionTreeClassifier(criterion = "entropy", random_state=0)
    # train model
    model.fit(xTrain, yTrain)
    # get acciracy
    accuracyTraining = model.score(xTrain, yTrain)
    accuracyTest = model.score(xTest, yTest)
    # get feature importances
    featureImportances = model.feature_importances_

    # check if the tree should be drawn
    if is_draw:
        print("Drawing tree...")
        # check if there is a drawing limit
        # draw tree
        if is_limit:
            export_graphviz(model, out_file='tree.dot', feature_names=["Freq", "Length", "SLQS"], filled=True,
                            class_names=["0", "1"], max_depth=depth)
        else:
            export_graphviz(model, out_file='tree.dot', feature_names=["Freq", "Length", "SLQS"], filled=True, class_names=["0", "1"])

        # save tree as .png
        call(['dot', '-T', 'png', 'tree.dot', '-o', 'tree.png'])
        print("Tree drawn and saved")

    return accuracyTraining, accuracyTest, featureImportances

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

