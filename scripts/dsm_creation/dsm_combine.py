import pickle
from tqdm import tqdm
from docopt import docopt


def main():
    args = docopt("""Combine multiple DSM's and word frequencies and save them
    
    Usage:
        dsm_combine.py <output_file_dsm> <output_file_freq> (<input_file>...)
        
    Arguments:
        <input_file> = pickled file storing the DSM and word frequencies as a tuple (dsm, wordFreq)
        <output_file_dsm> = file to save the pickled DSM
        <output_file_freq> = file to save the pickled word frequencies
        
    """)

    # get arguments
    input_files = args['<input_file>']
    output_file_dsm = args['<output_file_dsm>']
    output_file_freq = args['<output_file_freq>']

    loaded_input_files = []
    print("Loading files...")
    for input_file in tqdm(input_files):
        tuple = read_from_pickle(input_file)
        loaded_input_files.append(tuple)
    print("Loaded files")

    print("Combining...")
    dsmCombined, wordFreqCombined = combine_spaces(loaded_input_files)
    print("Combined")

    save_to_pickle(dsmCombined, output_file_dsm)
    save_to_pickle(wordFreqCombined, output_file_freq)
    print("Saved")


def combine_spaces(spaces: list):
    """
    Combine multiple DSM's and word frequency counts into one DSM
    :param spaces: list containing tuples of (dsm, word frequency)
    :return: dsm, word frequency
    """
    # set first dsm and word frequency counts as versions to be contain combinations
    spaceCombine = spaces[0]
    dsmCombine = spaceCombine[0]
    wordFrequencyCombine = spaceCombine[1]
    # combine all DSM's and word frequency counts into one
    for space in tqdm(spaces[1:]):
        dsm = space[0]
        wordFrequency = space[1]

        for word, freq in wordFrequency.items():
            # check if word already present
            if word in wordFrequencyCombine:
                # if yes, sum frequency counts
                wordFrequencyCombine[word] = wordFrequencyCombine[word] + freq
            # if not, add it with its frequency count
            else:
                wordFrequencyCombine[word] = freq

        for target, contexts in dsm.items():
            # check if target already present
            if target in dsmCombine:
                # if yes, process the contexts
                for context, freq in contexts.items():
                    # check if context already present for target
                    if context in dsmCombine[target]:
                        # if yes, sum co-occurence counts
                        dsmCombine[target][context] = dsmCombine[target][context] + freq
                    # if not, add it with its co-occurence count
                    else:
                        dsmCombine[target][context] = freq
            # if target not yet present, add it with its context vector
            else:
                dsmCombine[target] = dsm[target]

    return dsmCombine, wordFrequencyCombine


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
