import pickle
import math
from tqdm import tqdm
from docopt import docopt


def main():
    args = docopt("""Calculate SLQS Row and save results as dict

    Usage:
        slqsRow.py <dsm_file> <rowSums_file> <output_file_results> (<dataset_file>...)

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

    print("Calculating SLQS...")
    slqs = SLQS(dsm, rowSums)
    results = slqs.calculate_slqsRow(pairs)
    print("Calculated SLQS")

    save_to_pickle(results, output_file_results)
    print("Saved")



class SLQS:

    def __init__(self, dsm, rowSums):
        """
        
        :param dsm: 
        :param rowSums: 
        """
        self.dsm = dsm
        self.rowSums = rowSums

    def entropy(self, word: str):
        """
        Calculate word entropy
        :param word: the word
        :return: entropy of the word
        """
        entropy = 0
        wordCoocFreq = self.rowSums[word]

        # iterate over all contexts of the word
        for context, freq in self.dsm[word].items():
            probWordContext = freq / wordCoocFreq
            entropy += probWordContext * math.log2(probWordContext)

        entropy = -entropy
        return entropy

    def calculate_slqsRow(self, wordPairs: set):
        """
        Calculate SLQS Row as described in:
        Vered Shwartz, Enrico Santus, and Dominik Schlechtweg. 
        Hypernyms under siege: Linguistically-motivated artillery for hypernymy detection. 2016.
        :param wordPairs: the word pairs
        :return: SLQS Row results as dictionary
        """
        results = {}

        # iterate over all word pairs
        for pair in tqdm(wordPairs):
            hypo = pair[0]
            hyper = pair[1]
            # calculate entropy for hyponym and hypernym
            entropyHypo = self.entropy(hypo)
            entropyHyper = self.entropy(hyper)
            if entropyHypo != 0 and entropyHyper != 0:
                # calculate SLQS Row for both directions
                slqsRow1 = 1 - (entropyHypo / entropyHyper)
                slqsRow2 = 1 - (entropyHyper / entropyHypo)
                results[pair] = slqsRow1
                results[(hyper, hypo)] = slqsRow2
            else:
                # handle cases where the word entropy is zero
                if entropyHypo == 0:
                    results[pair] = 1
                    results[(hyper, hypo)] = -1
                if entropyHyper == 0:
                    results[pair] = -1
                    results[(hyper, hypo)] = 1

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