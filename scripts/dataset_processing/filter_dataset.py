import pickle
from tqdm import tqdm
from docopt import docopt


def main():
    args = docopt("""For a data set filter out irrelevant pairs, i.e. pairs that
    - are not included in the DSM
    - have no co-occurrences (row sum = 0)
    Save obtained data set
    Optionally split data set into compound-pairs and non-compound-pairs and save both sets
    
    
    Usage:
        filter_dataset.py <input_file_dataset> <rowSums_file> <output_file_dataset> [-s <output_file_dataset_compound> <output_file_dataset_nonCompound>]
        
    Arguments:
        <input_file_dataset> = file containing the data set (pickled)
        <rowSums_file> = file containing the row sums of the corpus (pickled)
        <output_file_dataset> = file to save the pickled data set
        <output_file_dataset_compound> = file to save the pickled compound-pairs
        <output_file_dataset_nonCompound> = file to save the pickled non-compound-pairs
        
    Options:
        -s --split  split dataset into compound-pairs and non-compound-pairs
    
    """)

    # get arguments and options
    input_file_dataset = args['<input_file_dataset>']
    rowSums_file = args['<rowSums_file>']
    output_file_dataset = args['<output_file_dataset>']
    output_file_dataset_compound = args['<output_file_dataset_compound>']
    output_file_dataset_nonCompound = args['<output_file_dataset_nonCompound>']
    is_split = args['--split']

    print("Loading row sums...")
    rowSums = read_from_pickle(rowSums_file)
    print("Loaded row sums")
    print("Loading data set...")
    dataset = read_from_pickle(input_file_dataset)
    print("Loaded data set")

    print("Filtering data set...")
    relevantPairs = relevant_pairs(dataset, rowSums)
    print("Number of relevant pairs: " + str(len(relevantPairs)))
    save_to_pickle(relevantPairs, output_file_dataset)
    print("Saved")

    if is_split:
        print("Splitting data set...")
        compounds, nonCompounds = split_dataset(relevantPairs)
        print("Number of compound-pairs: " + str(len(compounds)))
        print("Number of non-compound-pairs: " + str(len(nonCompounds)))
        save_to_pickle(compounds, output_file_dataset_compound)
        save_to_pickle(nonCompounds, output_file_dataset_nonCompound)
        print("Saved")


def relevant_pairs(wordPairs: set, rowSums):
    """
    Filter out irrelevant pairs
    :param wordPairs: set of word pairs
    :param rowSums: row sums
    :return: set of relevant word pairs
    """
    relevantPairs = set()
    notInSemanticSpace = 0
    noContext = 0
    bothDirections = 0
    for pair in tqdm(wordPairs):
        hypo = pair[0]
        hyper = pair[1]
        # check if both nouns are in the DSM
        if hypo in rowSums and hyper in rowSums:
            # check if both nouns have at least one context
            if rowSums[hypo] > 0 and rowSums[hyper] > 0:
                # check if the pair is included in both directions (is not filtered out)
                if (hyper, hypo) in wordPairs:
                    bothDirections += 1
                relevantPairs.add((hypo, hyper))
            else:
                noContext += 1
        else:
            notInSemanticSpace += 1

    print("Not in DSM: " + str(notInSemanticSpace))
    print("No co-occurrences: " + str(noContext))
    print("Included in both directions (e.g. (n1, n2) and (n2, n1)): " + str(bothDirections))

    return relevantPairs


def split_dataset(wordPairs: set):
    """
    Split a set of word pairs into compound-pairs and non-compound-pairs
    :param wordPairs: set of word pairs
    :return: compound-pairs, non-compound-pairs
    """
    compounds = set()
    nonCompounds = set()
    for pair in wordPairs:
        hypo = pair[0].split(" ")
        hypo = hypo[0]
        hyper = pair[1].split(" ")
        hyper = hyper[0]
        # check for substring inclusion
        if (hyper.casefold() in hypo.casefold()) or (hypo.casefold() in hyper.casefold()):
            compounds.add(pair)
        else:
            nonCompounds.add(pair)

    return compounds, nonCompounds


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
