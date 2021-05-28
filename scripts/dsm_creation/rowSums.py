import pickle
from tqdm import tqdm
from docopt import docopt


def main():
    args = docopt("""Calculate row sum for each target of the DSM and save it in dict
    
    Usage:
        rowSums.py <dsm_file> <output_file_rowSums>
        
    Arguments:
        <dsm_file> = file containing the pickled DSM
        <output_file_rowSums> = file to save the pickled rowSums dict
    
    """)

    # get arguments
    dsm = args['<dsm_file>']
    output_file_rowSums = args['<output_file_rowSums>']

    rowSums = row_sum(dsm)
    save_to_pickle(rowSums, output_file_rowSums)
    print("Row sums saved")


def row_sum(dsmFile: str):
    """
    Calculate row sums
    :param dsmFile: pickle file cotaining the DSM
    :return: row sums as dictionary
    """
    print("Loading DSM...")
    dsm = read_from_pickle(dsmFile)
    print("DSM loaded")
    rowSums = {}
    print("Calculating row sums")
    for target, context in tqdm(dsm.items()):
        # sum up all co-occurrence counts
        rowSum = sum(dsm[target].values())
        rowSums[target] = rowSum
    print("Row sums calculated")

    return rowSums

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
