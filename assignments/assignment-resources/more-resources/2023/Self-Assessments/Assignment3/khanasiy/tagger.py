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


    ####################
    # STUDENT CODE HERE
    ####################
    i = 0
    prior = []
    transition = []
    for t in UNIVERSAL_TAGS:
        prior.append(0)
        x = []
        for s in UNIVERSAL_TAGS:
            x.append(0)
        transition.append(x)
    emission = {}
    emission_2 = {}

    prev_tag = ""
    count = 0

    for (word, tag) in pos_data:

        # Increment the transition count for the previous word and tag
        if not count in sent_inds:
            transition[UNIVERSAL_TAGS.index(prev_tag)][UNIVERSAL_TAGS.index(tag)] += 1

        # Increment the emission count for the tag and word
        emission[(tag, word)] = emission.get((tag, word), 0) + 1
        emission_2[tag] = emission_2.get(tag, 0) + 1

        if count in sent_inds:
            # Increment the prior count
            prior_index = UNIVERSAL_TAGS.index(tag)
            prior[prior_index] += 1

        # Set the previous tag to this tag (for the next iteration of the loop)
        prev_tag = tag
        count += 1

    # fix prior
    total_prior = sum(prior)
    i = 0
    while i < len(prior):
        prior[i] = prior[i]/total_prior
        i += 1
    prior = np.log(prior)

    #fix transition
    i = 0
    while i < len(transition):
        total_trans = sum(transition[i])
        j = 0
        while j < len(transition[i]):
            transition[i][j] = (transition[i][j])/total_trans
            j += 1
        i += 1
    transition = np.log(transition)

    # fix emissions
    for (tag, word) in emission:
        emission[(tag, word)] = np.log(emission[(tag, word)]/emission_2[tag])

    return prior, transition, emission


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    # prior: prob of seeing i'th tag at beginning of sequence
    # transition: prob of seeing t[i][j] where j comes after i
    # emission: prob of seeing e[(tag, word)]

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    ####################
    # STUDENT CODE HERE
    ####################
    results = []

    i = 0
    prev_tag = "."
    index = len(UNIVERSAL_TAGS) - 1
    prior = list(prior)


    for word in pos_data:
        tag = UNIVERSAL_TAGS[0]
        maxim = -np.inf
        for tags in UNIVERSAL_TAGS:
            if emission.get((tags, word), -np.inf) + transition[index][UNIVERSAL_TAGS.index(tags)] > maxim:
                tag = tags
                maxim = emission[(tags, word)] + transition[index][UNIVERSAL_TAGS.index(tags)]
        if i in sent_inds:
            highest = max(prior)
            index = prior.index(highest)
            tags = UNIVERSAL_TAGS[index]
            if emission.get((tags, word), -np.inf) + transition[index][UNIVERSAL_TAGS.index(tags)] > maxim:
                tag = tags
                maxim = emission[(tags, word)] + transition[index][UNIVERSAL_TAGS.index(tags)]
        i += 1

        results.append(tag)

    write_results(test_file_name+'.pred', results)

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
