import pickle
from tqdm import tqdm
import math
from docopt import docopt


def main():
    args = docopt("""Compute PLMI values for all targets and their contexts of used data sets and save as dict[dict]
    
    Usage:
        plmi.py <dsm_file> <rowSums_file> <output_file_plmi> (<input_file_dataset>...)
        
    Arguments:
        <dsm_file> = file containing the pickled DSM
        <rowSums_file> = file containing the pickled row sums
        <output_file_plmi> = file containing the plmi values as dict[target:dict[context:plmi]]
        <input_file_dataset> = file containing the pickled filtered data set
    
    """)

    # get arguments
    dsm_file = args['<dsm_file>']
    rowSums_file = args['<rowSums_file>']
    output_file_plmi = args['<output_file_plmi>']
    input_file_dataset = args['<input_file_dataset>']

    print("Loading DSM...")
    dsm = read_from_pickle(dsm_file)
    print("Loaded DSM")

    print("Loading row sums...")
    rowSums = read_from_pickle(rowSums_file)
    print("Loaded row sums")

    print("Loading data set(s)...")
    pairs = set()
    for dataset_file in input_file_dataset:
        dataset = read_from_pickle(dataset_file)
        pairs = pairs | dataset
    print("Loaded data sets")

    print("Calculating PLMI values...")
    dsmPLMI = dsm_plmi(pairs, dsm, rowSums)
    print("Calculated PLMI values")

    save_to_pickle(dsmPLMI, output_file_plmi)
    print("Saved")


def sample_size(rowSums: dict):
    """
    Compute total number of all co-occurence counts, i.e. the sum of all row sums
    :param rowSums: the row sums
    :return: total number of all co-occurence counts
    """
    sampleSize = 0
    for target, freq in rowSums.items():
        sampleSize += freq

    return sampleSize


def plmi(dsm, target: str, context: str, sampleSize, rowSums: dict):
    """
    this function computes the plmi value for a target and a context word
    plmi (Positive Pointwise Mutual Information) as described in:
    Stefan Evert. The statistics of word cooccurrences: word pairs and collocations. 2005.
    :param dsm: the DSM as dictionary with [target:[context:co-occurrence count]]
    :param target: target word
    :param context: context word
    :param sampleSize: total sum of all row sums
    :param targetTotal: row sum of target
    :param rowSums: row sums as dictionary with [target:row sum]
    :return: plmi value
    """
    observedFreq = dsm[target][context]
    targetTotal = rowSums[target]
    contextTotal = rowSums[context]
    expectedFreq = (targetTotal * contextTotal) / sampleSize

    if expectedFreq == 0:
        plmi = 0
    else:
        plmi = observedFreq * math.log10(observedFreq / expectedFreq)
        if plmi < 0:
            plmi = 0
    return plmi


def dsm_plmi(wordPairs: set, dsm, rowSums):
    """
    Compute plmi scores for words and save in DSM format
    :param wordPairs: a set of word pairs
    :param dsm: the DSM
    :param rowSums: the row sums
    :return: DSM with plmi weighting (only for given words as targets)
    """
    sampleSize = sample_size(rowSums)
    dsmPLMI = {}

    for pair in tqdm(wordPairs):
        hypo = pair[0]
        hyper = pair[1]
        # check if target is already present
        if hypo not in dsmPLMI:
            hypoPlmis = {}
            if hypo not in rowSums:
                print(hypo + " not in DSM")
            else:
                # calculate plmi for all contexts and store them in dictionary
                for context in dsm[hypo].keys():
                    hypoPlmis[context] = plmi(dsm, hypo, context, sampleSize, rowSums)
                # set plmi dict as context vector for target
                dsmPLMI[hypo] = hypoPlmis

        # same as above for the hypernym of the word pair
        if hyper not in dsmPLMI:
            hyperPlmis = {}
            if hyper not in rowSums:
                print(hyper)
            else:
                for context in dsm[hyper].keys():
                    hyperPlmis[context] = plmi(dsm, hyper, context, sampleSize, rowSums)
                dsmPLMI[hyper] = hyperPlmis

    return dsmPLMI


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
