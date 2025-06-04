# The tagger.py starter code for CSC384 A4.
import math
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

    ####################
    # STUDENT CODE HERE
    ####################
    prior = [0] * N_tags
    for i in sent_inds:
        prior[UNIVERSAL_TAGS.index(pos_data[i][1])] += 1
    prior = np.log(np.divide(prior, np.sum(prior)))

    transition = [[0 for _ in range(N_tags)] for _ in range(N_tags)]
    tag_count = [0] * N_tags
    for start, end in zip(sent_inds, sent_inds[1:] + [len(pos_data)]):
        for i in range(start + 1, end):
            tag_i = UNIVERSAL_TAGS.index(pos_data[i - 1][1])
            tag_j = UNIVERSAL_TAGS.index(pos_data[i][1])
            tag_count[tag_i] += 1
            transition[tag_i][tag_j] += 1

    for i, _ in enumerate(UNIVERSAL_TAGS):
        transition[i] = np.divide(transition[i], tag_count[i])
    transition = np.log(transition)

    emission = {}
    for tag in UNIVERSAL_TAGS:
        word_list = [x for x in pos_data if x[1] == tag]
        for (word, _), count in Counter(word_list).items():
            emission[(tag, word)] = np.log(np.divide(count, len(word_list)))

    return prior, transition, emission


def get_emission(emission, tag, word):
    if emission.get((UNIVERSAL_TAGS[tag], word)) is None:
        return math.log(0.00001)
    else:
        return emission.get((UNIVERSAL_TAGS[tag], word))


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
    for start, end in zip(sent_inds, sent_inds[1:] + [len(pos_data)]):
        sentence = pos_data[start:end]
        prob_trellis = np.zeros((N_tags, len(sentence)))
        path_trellis = [[[] for _ in range(len(sentence))] for _ in range(N_tags)]

        for s in range(N_tags):
            prob_trellis[s, 0] = prior[s] + get_emission(emission, s, sentence[0])
            path_trellis[s][0] = [s]

        for o in range(1, len(sentence)):
            for s in range(N_tags):
                b = get_emission(emission, s, sentence[o])
                x = np.argmax(prob_trellis[:, o - 1] + transition[:, s] + b)
                prob_trellis[s, o] = prob_trellis[x, o - 1] + transition[x, s] + b
                path_trellis[s][o] = path_trellis[x][o - 1][:]
                path_trellis[s][o].append(s)

        path = path_trellis[np.argmax(prob_trellis[:, -1])][-1]

        for p in path:
            results.append(UNIVERSAL_TAGS[p])

    write_results(test_file_name + '.pred', results)


if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d") + 1]
    test_file_name = parameters[parameters.index("-t") + 1]
    #train_file_name = 'data/train-public'
    #test_file_name = 'data/test-public-small'

    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)

    #test_file_name = 'data/test-public-large'
    #tag(train_file_name, test_file_name)
