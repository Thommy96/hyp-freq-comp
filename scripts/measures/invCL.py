import pickle
from tqdm import tqdm
import math
from docopt import docopt


def main():
    args = docopt("""Calculate InvCL and save as dict

    Usage:
        invCL.py <dsm_file> <rowSums_file> <output_file_results> (<dataset_file>...)

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

    print("Calculating invCL...")
    results = inv_CL(dsm, rowSums, pairs)
    print("Calculated invCL")

    save_to_pickle(results, output_file_results)
    print("Saved")


def inv_CL(dsm, rowSums, wordPairs):
    """
    Calculate InvCL as described in:
    Alessandro Lenci and Giulia Benotto. Identifying hypernyms in distributional semantic spaces.
    In *SEM 2012
    :param dsm: the DSM
    :param rowSums: the row sums
    :param wordPairs: the word pairs
    :return: InvCL results as dictionary
    """
    results = {}
    # iterate over all word pairs
    for wordPair in tqdm(wordPairs):
        hypo = wordPair[0]
        hyper = wordPair[1]

        # clarkeDE
        # direction 1
        numerator = 0
        # get intersection of contexts of hyponym and hypernym
        contextIntersection = dsm[hypo].keys() & dsm[hyper].keys()
        # iterate over these common contexts
        for context in contextIntersection:
            # get the minimum and add it to the numerator
            numerator = numerator + min(dsm[hypo][context], dsm[hyper][context])

        # sum all frequencies of hyponym
        denominator = rowSums[hypo]

        # calculate clarkeDE
        clarkeDE1 = numerator / denominator


        # direction 2
        #the numerator stays the same
        # sum all frequencies of word2
        denominator = rowSums[hyper]

        # calculate clarkeDE
        clarkeDE2 = numerator / denominator

        # calculate invCL for both directions
        invCL = math.sqrt(clarkeDE1 * (1 - clarkeDE2))
        results[(hypo, hyper)] = invCL
        invCL = math.sqrt(clarkeDE2 * (1 - clarkeDE1))
        results[(hyper, hypo)] = invCL

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