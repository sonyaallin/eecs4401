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
    return [tuple(line.split(' : ')) for line in
            open(path, 'r').read().split('\n')[:-1]]


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
    emission = {}
    tags = {tag: 0 for tag in UNIVERSAL_TAGS}
    t_counts = {tag: 0 for tag in UNIVERSAL_TAGS}
    line = 0

    # prior
    prior = np.zeros(len(UNIVERSAL_TAGS))
    prior_dict = {tag: 0 for tag in UNIVERSAL_TAGS}
    # emission
    for tup in pos_data:
        pair = (tup[1], tup[0])
        if pair not in emission:
            emission[pair] = 1
        else:
            emission[pair] += 1
        if tup[1] in tags:
            tags[tup[1]] += 1
            if line + 1 not in sent_inds:
                t_counts[tup[1]] += 1
            if line in sent_inds:
                prior_dict[tup[1]] += 1
        line += 1
    t_counts["."] -= 1
    for wortag in emission:
        emission[wortag] = np.log(emission[wortag] / tags[wortag[0]])

    # prior cont
    for y, t in enumerate(UNIVERSAL_TAGS):
        prior[y] = (round(np.log(prior_dict[t] / len(sent_inds)), 8))

    # transition
    transition = np.zeros(shape=(len(UNIVERSAL_TAGS), len(UNIVERSAL_TAGS)))
    for i, tag1 in enumerate(UNIVERSAL_TAGS):
        for j, tag2 in enumerate(UNIVERSAL_TAGS):
            v = 0
            for x in range(len(pos_data) - 1):
                if pos_data[x][1] == tag1 and pos_data[x + 1][1] == tag2 and (
                        x + 1) not in sent_inds:
                    v += 1
            if v == 0:
                transition[i, j] = -float('inf')
            else:
                transition[i, j] = np.log(v / t_counts[tag1])

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
    # Π: initial probabilities. A: transition matrix. B: emission matrix.
    # s is UNIVERSAL TAGS
    # o are the words themselve
    lines = []
    prev = 0
    for l in sent_inds:
        line1 = pos_data[prev:l]
        lines.append(line1)
        prev = l
    lines.append(pos_data[prev:])
    lines.pop(0)
    results = []
    # Determine trellis values for X1
    for line in lines:
        prob_trellis = np.zeros(shape=(len(UNIVERSAL_TAGS), len(line)))
        path_trellis = np.zeros([len(UNIVERSAL_TAGS), len(line)], dtype=list)
        for s in range(len(UNIVERSAL_TAGS)):
            prob_trellis[s, 0] = prior[s] + emission.get(
                (UNIVERSAL_TAGS[s], line[0]), np.log(0.00001))
            path_trellis[s][0] = [UNIVERSAL_TAGS[s]]
        # For X2-XT find each current state's most likely prior state x.
        for o in range(1, len(line)):
            for s in range(len(UNIVERSAL_TAGS)):
                x = np.argmax(prob_trellis[:, o - 1] + transition[:, s])
                prob_trellis[s, o] = prob_trellis[x, o - 1] + transition[x, s] + \
                                     emission.get((UNIVERSAL_TAGS[s], line[o]),
                                                  np.log(0.00001))
                path_trellis[s][o] = path_trellis[x][o - 1] + [
                    UNIVERSAL_TAGS[s]]
        max_value = np.argmax(prob_trellis[:, -1])
        path = path_trellis[max_value][-1]
        results.extend(path)

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
