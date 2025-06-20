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

    pos_data = read_data_train(train_file_name + '.txt')
    sent_inds = read_data_ind(train_file_name + '.ind')

    sent_num_total = len(sent_inds)  # get total number of sentences
    sent_start_tag = Counter([pos_data[i][1] for i in sent_inds])  # get the POS_TAG of the start of each sentence

    # create and fill prior
    prior = np.zeros(N_tags)
    for i in range(N_tags):
        curr = sent_start_tag[UNIVERSAL_TAGS[i]]
        if curr != 0:
            prior[i] = np.log((curr / sent_num_total))
        else:
            prior[i] = curr

    # create and fill transtition
    transition = np.zeros((N_tags, N_tags))
    for i in range(len(sent_inds) - 1):
        s = pos_data[sent_inds[i]:sent_inds[i + 1]]
        for j in range(len(s) - 1):
            curr_tag = s[j][1]
            curr_next_tag = s[j + 1][1]
            curr_ind = UNIVERSAL_TAGS.index(curr_tag)
            curr_next_tag_ind = UNIVERSAL_TAGS.index(curr_next_tag)
            if curr_ind is not None and curr_next_tag_ind is not None:
                transition[curr_ind, curr_next_tag_ind] += 1
    # last sentence remaining
    s = pos_data[sent_inds[-1]:]
    for j in range(len(s) - 1):
        curr_tag = s[j][1]
        curr_next_tag = s[j + 1][1]
        curr_ind = UNIVERSAL_TAGS.index(curr_tag)
        curr_next_tag_ind = UNIVERSAL_TAGS.index(curr_next_tag)
        if curr_ind is not None and curr_next_tag_ind is not None:
            transition[curr_ind, curr_next_tag_ind] += 1
    for i in range(N_tags):
        transition[i] /= sum(transition[i])
    transition = np.log(transition)

    occ_all_tags = Counter(i[1] for i in pos_data)  # get the number of times each tag occurs
    # create an fill emission dict
    emission = dict()
    word_tag_counts = Counter(pos_data)
    for p in word_tag_counts:
        x = occ_all_tags[p[1]]
        emission[(p[1], p[0])] = np.log((word_tag_counts[p] / x))

    return prior, transition, emission

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name + '.txt')
    sent_inds = read_data_ind(test_file_name + '.ind')

    ####################
    # STUDENT CODE HERE
    ####################
    results = []
    write_results(test_file_name + '.pred', results)


if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d") + 1]
    test_file_name = parameters[parameters.index("-t") + 1]

    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)
