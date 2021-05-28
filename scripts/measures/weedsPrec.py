import pickle
from tqdm import tqdm
import math
from docopt import docopt


def main():
    args = docopt("""Calculate WeedsPrec and save as dict
    
    Usage:
        weedsPrec.py <dsm_file> <rowSums_file> <output_file_results> (<dataset_file>...)
        
    Arguments:
        <dsm_file> = file containing the pickled DSM
        <rowSums_file> = file containing the pickled row sums
        <dataset_file> = file containing the pickled data set
        <output_file_results> = file to save the pickled results
    
    """)

    # get arguments
    dsm_file = args['<dsm_file>']
    rowSums_file = args['<rowSums_file>']
    dataset_file = args['<dataset_file>']
    output_file_results = args['<output_file_results>']

    print("Loading DSM...")
    dsm = read_from_pickle(dsm_file)
    print("Loaded DSM")

    print("Loading row sums...")
    rowSums = read_from_pickle(rowSums_file)
    print("Loaded row sums")

    print("Loading data set(s)...")
    pairs = set()
    for data in dataset_file:
        dataset = read_from_pickle(data)
        pairs = pairs | dataset
    print("Loaded data sets")

    print("Calculating WeedsPrec...")
    results = weeds_prec(dsm, rowSums, pairs)
    print("Calculated WeedsPrec")

    save_to_pickle(results, output_file_results)
    print("Saved")


def weeds_prec(dsm, rowSums, wordPairs):
    """
    Calculate Weeds Precision as described in:
    Julie Weeds, David Weir, and Diana McCarthy. Characterising measures of lexical distributional similarity.
    InProceedings of the 20th international conference on Computational Linguistics, page 1015. 
    Association for Computational Linguistics, 2004
    :param dsm: the DSM
    :param rowSums: the row sums
    :param wordPairs: the word pairs
    :return: WeedsPrec results as dictionary
    """
    results = {}
    # iterate over all word pairs
    for wordPair in tqdm(wordPairs):
        hypo = wordPair[0]
        hyper = wordPair[1]

        # direction 1
        numerator = 0
        # get intersection of contexts of hyponym and hypernym
        contextIntersection = dsm[hypo].keys() & dsm[hyper].keys()
        # iterate over these common contexts
        for context in contextIntersection:
            # sum all co-occurrence frequencies of hyponym for common contexts
            numerator = numerator + dsm[hypo][context]

        # sum all frequencies of hyponym
        denominator = rowSums[hypo]

        # calculate WeedsPrec
        weedsPrec = numerator / denominator
        results[(hypo, hyper)] = weedsPrec

        # direction 2, same as for direction 1, but with switched roles of hyponym and hypernym
        numerator = 0

        contextIntersection = dsm[hyper].keys() & dsm[hypo].keys()
        for context in contextIntersection:
            numerator = numerator + dsm[hyper][context]

        denominator = rowSums[hyper]

        weedsPrec = numerator / denominator
        results[(hyper, hypo)] = weedsPrec

    return results


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
