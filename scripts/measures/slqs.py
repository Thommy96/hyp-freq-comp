import pickle
import math
import statistics
from collections import OrderedDict
from operator import itemgetter
from tqdm import tqdm
from docopt import docopt

def main():
    args = docopt("""Calculate SLQS and save results as dict
    
    Usage:
        slqs.py <dsm_file> <plmi_file> <rowSums_file> <top_N> <output_file_results> (<dataset_file>...)
        
    Arguments:
        <dsm_file> = file containing the pickled DSM
        <plmi_file> = file containing the pickled plmi values
        <top_N> = integer setting the top N contexts for second order word entropy
        <rowSums_file> = file containing the pickled row sums
        <dataset_file> = file containing the pickled data set
        <output_file_results> = file to save the pickled results
    
    """)

    #get arguments
    dsm_file = args['<dsm_file>']
    plmi_file = args['<plmi_file>']
    rowSums_file = args['<rowSums_file>']
    topN = int(args['<top_N>'])
    dataset_file = args['<dataset_file>']
    output_file_results = args['<output_file_results>']

    print("Loading DSM...")
    dsm = read_from_pickle(dsm_file)
    print("Loaded DSM")

    print("Loading plmi...")
    plmi = read_from_pickle(plmi_file)
    print("Loaded plmi")

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
    slqs = SLQS(dsm, plmi, rowSums, topN)
    results = slqs.calculate_slqs(pairs)
    print("Calculated SLQS")

    save_to_pickle(results, output_file_results)
    print("Saved")


def sample_size(rowSums:dict):
    """
    Compute total number of all co-occurence counts, i.e. the sum of all row sums
    :param rowSums: the row sums
    :return: total number of all co-occurence counts
    """
    sampleSize = 0
    for target, freq in rowSums.items():
        sampleSize += freq

    return sampleSize

class SLQS:

    entropyDict = {}
    medianEntropy = {}

    def __init__(self, dsm, dsmPLMI, rowSums, topN):
        """
        
        :param dsm: the DSM
        :param dsmPLMI: the Positive Local Mutual Information values
        :param rowSums: the row sums
        :param topN: number of top contexts for second order word entropy
        """
        self.dsm = dsm
        self.dsmPLMI = dsmPLMI
        self.rowSums = rowSums
        self.sampleSize = sample_size(self.rowSums)
        self.topN = topN

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

    def top_N_contexts(self, word: str):
        """
        Get the top N contexts for a target word
        :param word: the target word
        :return: top N context for the target word
        """
        plmis = {}
        # iterate over all contexts of the target
        for context, plmi in self.dsmPLMI[word].items():
            # ignore context with plmi = 0
            if plmi > 0:
                plmis[context] = plmi

        # sort plmi values and get top N
        topN = dict(list(OrderedDict(sorted(plmis.items(), key=itemgetter(1), reverse=True)).items())[:self.topN])

        return topN

    def median_entropy_top_contexts(self, topContexts: dict):
        """
        Calculate median entropy of the top N contexts
        :param topContexts: top N contexts
        :return: median entropy
        """
        entropies = {}
        # iterate over top contexts
        for context, plmi in topContexts.items():
            # check if entropy already calculated
            # if not, calculate and store in dictionary
            if context not in self.entropyDict:
                self.entropyDict[context] = self.entropy(context)
            # get entropy of context
            entropies[context] = self.entropyDict[context]
        # claculate median entropy
        if len(entropies) != 0:
            medianEntropy = statistics.median(entropies.values())
        else:
            medianEntropy = 0

        return medianEntropy

    def second_order_entropy(self, word: str):
        """
        Calculate second order word entropy
        :param word: the word
        :return: second order word entropy
        """
        # get top N contexts for word
        topContexts = self.top_N_contexts(word)
        # claculate median entropy for top N contexts of word
        medianEntropyWord = self.median_entropy_top_contexts(topContexts)

        return medianEntropyWord

    def calculate_slqs(self, wordPairs:set):
        """
        Calculate SLQS as described in:
        Enrico Santus, Alessandro Lenci, Qin Lu, and Sabine Schulte Im Walde.
        Chasing hypernyms in vector spaces with entropy. 
        In Proceedings of the 14th Conference of the European Chapter of the Association for Computational Linguistics,
        volume 2: Short Papers, pages 38–42, 2014.
        :param wordPairs: the word pairs
        :return: SLQS results as dictionary
        """
        # sort word pairs for faster processing
        wordPairs = list(wordPairs)
        wordPairs = sorted(wordPairs)
        wordPairs = set(wordPairs)
        results = {}

        # iterate over word pairs
        for wordPair in tqdm(wordPairs):
            hypo = wordPair[0]
            hyper = wordPair[1]
            # check if second order wntropy already calculated, if not calculate it
            if hypo not in self.medianEntropy:
                self.medianEntropy[hypo] = self.second_order_entropy(hypo)
            if hyper not in self.medianEntropy:
                self.medianEntropy[hyper] = self.second_order_entropy(hyper)

            # calculate SLQS for both directions
            if self.medianEntropy[hypo] != 0 and self.medianEntropy[hyper] != 0:
                slqs1 = 1 - (self.medianEntropy[hypo] / self.medianEntropy[hyper])
                slqs2 = 1 - (self.medianEntropy[hyper] / self.medianEntropy[hypo])
                results[(hypo, hyper)] = slqs1
                results[(hyper, hypo)] = slqs2
            # handle cases, where second order entropy = 0
            else:
                if self.medianEntropy[hypo] == 0:
                    results[wordPair] = 1
                    results[(hyper, hypo)] = -1
                if self.medianEntropy[hyper] == 0:
                    results[wordPair] = -1
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