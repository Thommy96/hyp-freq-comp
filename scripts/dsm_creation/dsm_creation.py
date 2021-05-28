import pickle
from tqdm import tqdm
from docopt import docopt
import gzip


def main():
    args = docopt("""Create DSM for a corpus and save it along with word frequencies
    
    Usage:
        dsm_creation.py (-g | -e) <corpus_file> <window_size> (-s <output_file_dsm> <output_file_freq> | -c <output_file_tuple>)
        
    Arguments:
        <corpus_file> = a directory path referring to the corpus file to be processed, either deWac or pUkWac
        <window_size> = the window size for co-occurrence counting
        <output_file_dsm> = file to save the pickled DSM
        <output_file_freq> = file to save the pickled word frequencies
        <output_file_tuple> = file to save the pickled tuple (dsm, wordFreq)
        
    Options:
        -g --german  for German corpus
        -e --english  for English corpus
        -s --single  if corpus is in a single file
        -c --combine  if this is just a part of the corpus, that needs to be combined with the other parts later
        
    """)

    # get arguments and options
    corpus_file = args['<corpus_file>']
    window_size = int(args['<window_size>'])
    output_file_dsm = args['<output_file_dsm>']
    output_file_freq = args['<output_file_freq>']
    output_file_tuple = args['<output_file_tuple>']
    is_german = args['--german']
    is_english = args['--english']
    is_single = args['--single']
    is_combine = args['--combine']

    if is_german:
        print("Processing corpus..")
        dsm, wordFreq = semantic_space_german(corpus_file, window_size)
        print("Corpus processed")
        if is_single:
            save_to_pickle(dsm, output_file_dsm)
            save_to_pickle(wordFreq, output_file_freq)
            print("DSM saved, Word Frequency saved")
        if is_combine:
            save_to_pickle((dsm, wordFreq), output_file_tuple)
            print("(DSM, Word Frequency) saved, needs to be combined with other parts")
    if is_english:
        print("Processing corpus..")
        dsm, wordFreq = semantic_space_english(corpus_file, window_size)
        print("Corpus processed")
        if is_single:
            save_to_pickle(dsm, output_file_dsm)
            save_to_pickle(wordFreq, output_file_freq)
            print("DSM saved, Word Frequency saved")
        if is_combine:
            save_to_pickle((dsm, wordFreq), output_file_tuple)
            print("(DSM, Word Frequency) saved, needs to be combined with other parts")


def semantic_space_german(corpus: str, windowSize: int):
    """
    Computes the DSM and word frequency counts from a corpus file for German (dewac)
    :param corpus: the corpus file (.txt) (dewac)
    :param windowSize: the window size
    :return: dsm, word frequency
    """
    with open(corpus) as corpus:
        dsm = {}
        wordFrequency = {}
        # checks if the sentence is complete
        sentenceComplete = False
        # store sentence as a list
        sentence = []

        # only go one time through the corpus, read one word at a time, total as estimate for tqdm bar
        for word in tqdm(corpus, total=1196895401):
            word = word.strip()

            # "<s>" marks the beginning of a sentence, set sentence empty, sentence is not complete
            if word == "<s>":
                sentence = []
                sentenceComplete = False

            # "</s>" marks the end of a sentence, sentence is complete
            if word == "</s>":
                sentenceComplete = True

            # first column: word, second column: tag, third column: lemma
            word = word.split("\t")

            # add lemma with pos-tag to the sentence, only take into account nouns verbs and adjectives
            if (len(word) >= 3) and (word[1].startswith("N") or word[1].startswith("V") or word[1].startswith("ADJ")):
                lemma = word[2] + " " + word[1][0].lower()
                sentence.append(lemma)

            if sentenceComplete:

                # keep track of the index of the current word
                wordIndex = 0
                # go through the sentence word by word
                for lemma in sentence:
                    # ignore <unknown> lemmas, they should not be in the dsm
                    if lemma.startswith("<unknown>"):
                        continue
                    # if lemma not in word frequency dict, add and set count to 1
                    if lemma not in wordFrequency:
                        wordFrequency[lemma] = 1
                    # if lemma already in word frequency dict, add 1 to its count
                    else:
                        wordFrequency[lemma] += 1

                    # if lemma not yet in dsm, add it with an empty dictionary
                    if lemma not in dsm:
                        dsm[lemma] = {}

                    # keep track of the window size, should not start with the current lemma itself
                    tempIndex = wordIndex - 1
                    # check if tempIndex is within the window size and max. the beginning of the sentence
                    while (tempIndex >= 0 and wordIndex - tempIndex <= windowSize):
                        # avoid adding <unknown> lemmas to the DSM
                        if not sentence[tempIndex].startswith("<unknown>"):
                            # check if lemma already has an entry for this word
                            if not dsm.get(lemma).get(sentence[tempIndex]):
                                # if not, add it and set it to 1
                                dsm[lemma][sentence[tempIndex]] = 1
                            # if yes, add 1 to its count
                            else:
                                dsm[lemma][sentence[tempIndex]] += 1

                        # one word to the left
                        tempIndex -= 1

                    # same as above, but to the right of the current lemma
                    tempIndex = wordIndex + 1
                    while (tempIndex < len(sentence) and tempIndex - wordIndex <= windowSize):
                        if not sentence[tempIndex].startswith("<unknown>"):
                            if not dsm.get(lemma).get(sentence[tempIndex]):
                                dsm[lemma][sentence[tempIndex]] = 1
                            else:
                                dsm[lemma][sentence[tempIndex]] += 1

                        tempIndex += 1

                    # update word index for next iteration
                    wordIndex += 1

                sentenceComplete = False

    return dsm, wordFrequency


def semantic_space_english(corpusPath: str, windowSize: int):
    """
    Computes the DSM and word frequency counts from a corpus file for English (pukwac)
    :param corpusPath: the corpus file (.gz) (pukwac)
    :param windowSize: the window size
    :return: dsm, word frequency
    """
    dsm = {}
    wordFrequency = {}
    with gzip.open(corpusPath, "rt", encoding="latin1") as corpus:
        # checks if the sentence is complete
        sentenceComplete = False
        # store sentence as a list
        sentence = []

        # only go one time through the corpus, read one word at a time, total as estimate for tqdm bar
        for word in tqdm(corpus, total=500000000):
            word = word.strip()

            # "<s>" marks the beginning of a sentence, set sentence empty, sentence is not complete
            if word == "<s>":
                sentence = []
                sentenceComplete = False

            # "</s>" marks the end of a sentence, sentence is complete
            if word == "</s>":
                sentenceComplete = True

            # first column: word, second column: tag, third column: lemma
            word = word.split("\t")

            # add lemma with pos-tag to the sentence, only take into account nouns verbs and adjectives
            if (len(word) >= 3) and (word[2].startswith("N") or word[2].startswith("V") or word[2].startswith("J")):
                lemma = word[1] + " " + word[2][0].lower()
                sentence.append(lemma)

            if sentenceComplete:

                # keep track of the index of the current word
                wordIndex = 0
                # go through the sentence word by word
                for lemma in sentence:
                    # if lemma not in word frequency dict, add and set count to 1
                    if lemma not in wordFrequency:
                        wordFrequency[lemma] = 1
                    # if lemma already in word frequency dict, add 1 to its count
                    else:
                        wordFrequency[lemma] += 1

                    # if lemma not yet in dsm, add it with an empty dictionary
                    if lemma not in dsm:
                        dsm[lemma] = {}

                    # keep track of the window size, should not start with the current lemma itself
                    tempIndex = wordIndex - 1
                    # check if tempIndex is within the window size and max. the beginning of the sentence
                    while (tempIndex >= 0 and wordIndex - tempIndex <= windowSize):
                        # check if lemma already has an entry for this word
                        if not dsm.get(lemma).get(sentence[tempIndex]):
                            # if not, add it and set it to 1
                            dsm[lemma][sentence[tempIndex]] = 1
                        # if yes, add 1 to its entry
                        else:
                            dsm[lemma][sentence[tempIndex]] += 1

                        # one word to the left
                        tempIndex -= 1

                    # same as above, but to the right of the current lemma
                    tempIndex = wordIndex + 1
                    while (tempIndex < len(sentence) and tempIndex - wordIndex <= windowSize):
                        if not dsm.get(lemma).get(sentence[tempIndex]):
                            dsm[lemma][sentence[tempIndex]] = 1
                        else:
                            dsm[lemma][sentence[tempIndex]] += 1

                        tempIndex += 1

                    # update word index for next iteration
                    wordIndex += 1

                sentenceComplete = False
    return dsm, wordFrequency


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
