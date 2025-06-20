# The tagger.py starter code for CSC384 A4.

import os
import sys

import numpy as np
import random
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


def get_counts(data):
    tag_dict = {}
    for line in data:
        if line[1] not in tag_dict:
            tag_dict[line[1]] = 1
        else:
            tag_dict[line[1]] += 1
    return tag_dict


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
    num_words = len(pos_data)
    tag_dict = get_counts(pos_data)

    prior = []
    transition = []
    emission = {}

    # Populate prior array
    for utag in UNIVERSAL_TAGS:
        prior_cnt = 0
        for index in sent_inds:
            if (pos_data[index][1] == utag):
                prior_cnt += 1
        prior.append(np.log(prior_cnt/len(sent_inds)))

    # Populate transition array
    for tag1 in UNIVERSAL_TAGS:
        trans_sub = []
        for tag2 in UNIVERSAL_TAGS:
            union_cnt = 0
            tag1_cnt = 0
            ind_cnt = 1
            for i in range(1, num_words):

                if (ind_cnt < len(sent_inds)) and (i-1 == sent_inds[ind_cnt]-1):
                    ind_cnt += 1
                else:
                    if (pos_data[i-1][1] == tag1 and pos_data[i][1] == tag2):
                        union_cnt += 1
                    if(pos_data[i-1][1] == tag1):
                        tag1_cnt += 1

            cond = (union_cnt / (num_words - 1)) / (tag1_cnt / (num_words))
            trans_sub.append(np.log(cond))

        transition.append(np.array(trans_sub))

    # Populate emission dictionary
    cnt_dict = {}
    for line in pos_data:
        if (line[1], line[0]) not in cnt_dict:
            cnt_dict[(line[1], line[0])] = 1
        else:
            cnt_dict[(line[1], line[0])] += 1
    for tup in cnt_dict:
        tup_prob = cnt_dict[tup] / len(pos_data)
        tag_prob = tag_dict[tup[0]] / len(pos_data)
        emission[tup] = np.log(tup_prob / tag_prob)

    prior1 = np.array(prior)
    trans1 = np.array(transition)
    return prior1, trans1, emission


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')
    results = []

    # ---- CHECK FIRST ELEMENT ----
    tag_result = None
    max_prob = None
    for i in range(0, len(UNIVERSAL_TAGS)):
        utag = UNIVERSAL_TAGS[i]
        if (utag, pos_data[0]) in emission:

            if max_prob is None or abs(emission[(utag, pos_data[0])]) <= max_prob:
                max_prob = abs(emission[(utag, pos_data[0])] + prior[i])
                tag_result = utag

    if (tag_result is None):
        tag_result = UNIVERSAL_TAGS[random.randint(0, 11)]
    results.append(tag_result)

    # ---- CHECK REST ELEMENTS ----
    for i in range(1, len(pos_data)):
        tag_result = None
        max_prob = None

        for j in range(0, len(UNIVERSAL_TAGS)):
            utag1 = UNIVERSAL_TAGS[j]
            if (utag1, pos_data[i]) in emission:
                temp_prob = abs(emission[(utag1, pos_data[i])])

                if max_prob is None or temp_prob <= max_prob:
                    max_prob = temp_prob
                    tag_result = utag1

        if (tag_result is None):
            tag_result = UNIVERSAL_TAGS[random.randint(0, 11)]

        results.append(tag_result)

    write_results(test_file_name+'.pred', results)
    return results


if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d")+1]
    test_file_name = parameters[parameters.index("-t")+1]

    # Start the training and tagging operation.
    # RUN: python tagger.py -d data/train-public -t data/test-public-small
    tag(train_file_name, test_file_name)



