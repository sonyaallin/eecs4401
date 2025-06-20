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

UNIVERSAL_TAG_LOOKUP = {k: v for v, k in enumerate(UNIVERSAL_TAGS)}


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
    pos_data = read_data_train(f'{train_file_name}.txt')
    sent_inds = read_data_ind(f'{train_file_name}.ind')
    sent_inds += [len(pos_data)]

    prior_counter = Counter()
    previous_counter = Counter()
    transition = np.zeros((N_tags, N_tags))
    emissions_by_tag = [{} for _ in range(N_tags)]

    for i in range(len(sent_inds) - 1):
        prior_counter[pos_data[sent_inds[i]][1]] += 1

        skip_first = True
        for j in range(sent_inds[i], sent_inds[i + 1]):
            current_tag = UNIVERSAL_TAG_LOOKUP[pos_data[j][1]]
            emissions_by_tag[current_tag][pos_data[j][0]] = emissions_by_tag[current_tag].get(pos_data[j][0], 0) + 1

            if skip_first:
                skip_first = False
            else:
                previous_tag = pos_data[j - 1][1]
                previous_counter[previous_tag] += 1
                transition[UNIVERSAL_TAG_LOOKUP[previous_tag], current_tag] += 1

    sent_inds.pop()

    prior = np.zeros(N_tags)
    previous = np.zeros(N_tags)
    emission = {}

    for i in range(N_tags):
        prior[i] = prior_counter[UNIVERSAL_TAGS[i]] / len(sent_inds)
        previous[i] = previous_counter[UNIVERSAL_TAGS[i]]

        tag_total = sum(emissions_by_tag[i].values())
        for word, count in emissions_by_tag[i].items():
            emission[(UNIVERSAL_TAGS[i], word)] = np.log(count / tag_total)

    return np.log(prior), np.log(transition.T / previous).T, emission


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

    # write_results(test_file_name + '.pred', results)


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
