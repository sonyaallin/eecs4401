# The tagger.py starter code for CSC384 A4.

import os
import sys

import numpy as np
from collections import Counter

UNIVERSAL_TAGS = [
    "VERB",
    "NOUN",
    "PRON",
    "ADJ",
    "ADV",
    "ADP",
    "CONJ",
    "DET",
    "NUM",
    "PRT",
    "X",
    ".",
]

N_tags = len(UNIVERSAL_TAGS)


def read_data_train(path):
    return [tuple(line.split(' : ')) for line in open(path, 'r').read().split('\n')[:-1]]


def read_data_test(path):
    return open(path, 'r').read().split('\n')[:-1]


def read_data_ind(path):
    return [int(line) for line in open(path, 'r').read().split('\n')[:-1]]


def write_results(path, results):
    with open(path, 'w') as f:
        f.write('\n'.join(results))


def train_HMM(train_file_name):
    """
    Estimate HMM parameters from the provided training data.

    Input: Name of the training files. Two files are provided to you:
            - file_name.txt: Each line contains a pair of word and its Part-of-Speech (POS) tag
            - fila_name.ind: The i'th line contains an integer denoting the starting index of the i'th sentence in the text-POS data above

    Output: Three pieces of HMM parameters stored in LOG PROBABILITIES :

            - prior:        - An array of size N_tags
                            - Each entry corresponds to the prior log probability of seeing the i'th tag in UNIVERSAL_TAGS at the beginning of a sequence
                            - i.e. prior[i] = log P(tag_i)

            - transition:   - A 2D-array of size (N_tags, N_tags)
                            - The (i,j)'th entry stores the log probablity of seeing the j'th tag given it is a transition coming from the i'th tag in UNIVERSAL_TAGS
                            - i.e. transition[i, j] = log P(tag_j|tag_i)

            - emission:     - A dictionary type containing tuples of (str, str) as keys
                            - Each key in the dictionary refers to a (TAG, WORD) pair
                            - The TAG must be an element of UNIVERSAL_TAGS, however the WORD can be anything that appears in the training data
                            - The value corresponding to the (TAG, WORD) key pair is the log probability of observing WORD given a TAG
                            - i.e. emission[(tag, word)] = log P(word|tag)
                            - If a particular (TAG, WORD) pair has never appeared in the training data, then the key (TAG, WORD) should not exist.

    Hints: 1. Think about what should be done when you encounter those unseen emission entries during deccoding.
           2. You may find Python's builtin Counter object to be particularly useful 
    """

    pos_data = read_data_train(train_file_name+'.txt')
    sent_inds = read_data_ind(train_file_name+'.ind')

    #####################
    # STUDENT CODE HERE #
    #####################

    word_list = []
    tag_list = []
    for tup in pos_data:
        word_list.append(tup[0])
        tag_list.append(tup[1])
    counter_tags = Counter(tag_list)

    word_list = []
    tag_list = []
    for index in sent_inds:
        word_list.append(pos_data[index][0])
        tag_list.append(pos_data[index][1])
    counter_init_tags = Counter(tag_list)

    # PRIOR
    prior = []
    for tag in UNIVERSAL_TAGS:
        if tag in counter_init_tags:
            prior.append(np.log(counter_init_tags.get(tag) / len(sent_inds)))
        else:
            prior.append(0)
    prior = np.array(prior)

    # TRANSITION: Making a 12x12 matrix with all values initialized as 0
    transition = np.zeros((len(UNIVERSAL_TAGS), len(UNIVERSAL_TAGS)))
    for i in range(len(sent_inds)):
        start_index = sent_inds[i]
        end_index = sent_inds[i+1] if i < len(sent_inds)-1 else len(pos_data)
        for j in range(start_index, end_index-1):
            A = UNIVERSAL_TAGS.index(pos_data[j][1])
            B = UNIVERSAL_TAGS.index(pos_data[j+1][1])
            transition[A][B] += 1
    # Converting transition matrix values from count to log(prob)
    for i in range(len(transition)):
        denominator = sum(transition[i])
        for j in range(len(transition[i])):
            numerator = transition[i][j]
            if numerator > 0 and denominator > 0:
                transition[i][j] = np.log(transition[i][j] / denominator)
            else:
                transition[i][j] = -float('inf')

    # EMISSION: Making empty dictioanry
    emission = {}
    for tup in pos_data:
        key = (tup[1], tup[0])
        emission.setdefault(key, 0)
        emission[key] += 1
    # Converting emission dictionary values from count to log(prob)
    for key in emission:
        denominator = counter_tags.get(key[0])
        emission[key] = np.log(emission[key] / denominator)

    return prior, transition, emission


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """
    #####################
    # STUDENT CODE HERE #
    #####################
    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    results = []

    for i in range(len(sent_inds)):
        start_index = sent_inds[i]
        end_index = sent_inds[i+1] if i < len(sent_inds)-1 else len(pos_data)

        tag_index = _get_tag(pos_data[start_index], prior, emission)
        results.append(UNIVERSAL_TAGS[tag_index])

        for j in range(start_index+1, end_index):
            tag_index = _get_tag(pos_data[j], transition[tag_index], emission)
            results.append(UNIVERSAL_TAGS[tag_index])
    
    write_results(test_file_name+'.pred', results)


def _get_tag(word, prob_list, emission):
    """
        === HELPER FUNCTION for tag() ===
        Returns the index of the tag that word has the highest 
        probability of being based on values in 'prior'
    """
    max_prob = -float('inf')
    max_tag = -1
    for i in range(len(prob_list)):
        key = (UNIVERSAL_TAGS[i], word)
        if key in emission and (emission[key] * prob_list[i]) > max_prob:
            max_prob = (emission[key] * prob_list[i])
            max_tag = i
    if max_tag == -1:
        max_tag = np.argmax(prob_list)
    return max_tag


if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d")+1]
    test_file_name = parameters[parameters.index("-t")+1]

    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)
