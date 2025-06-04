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

    ####################
    # STUDENT CODE HERE
    ####################

    dic_tag = dict.fromkeys(UNIVERSAL_TAGS, 0)
    count = 0
    emission = {}

    pos_data = read_data_train(train_file_name + '.txt')
    sent_inds = read_data_ind(train_file_name + '.ind')

    for key in pos_data:
        emission[key[1], key[0]] = 0

    for u_tag in dic_tag:
        dic_tag[u_tag] = count
        count += 1

    count_words, all_tags = (zip(*pos_data))
    count_pairs = Counter(pos_data)
    count_tags = Counter(all_tags)
    prior = np.array([0] * N_tags)
    transition = np.zeros((N_tags, N_tags))
    tag_pairs = {}
    for tup in emission:
        emission[tup] = np.log(
            count_pairs[(tup[1], tup[0])] / count_tags[tup[0]])

    last_tag = pos_data[len(pos_data) - 1][1]
    count_tags[last_tag] -= 1

    for count in range(len(pos_data) - 1):
        cur_tag, next_tag = pos_data[count][1], pos_data[count + 1][1]
        # current tag and next tag
        if count == len(pos_data) - 2:  # account for last word
            if (count + 1) in sent_inds:
                prior[dic_tag[next_tag]] += 1
        if count in sent_inds:
            prior[dic_tag[cur_tag]] += 1
        if (count + 1) in sent_inds:
            continue
        if (cur_tag, next_tag) not in tag_pairs:
            tag_pairs[(cur_tag, next_tag)] = 0
        tag_pairs[(cur_tag, next_tag)] += 1

    for key in tag_pairs:
        transition[dic_tag[key[0]], dic_tag[key[1]]] = tag_pairs.get(key)

    priors = convert_prior(prior)
    transition = convert_transition(transition)
    return priors, transition, emission


def convert_transition(table):
    """Helper function to transform transition matrix to log probabilities with
    smoothening """
    probabilities = np.zeros((N_tags, N_tags))
    for row in range(N_tags):
        for col in range(N_tags):
            probabilities[row, col] = np.log(
                (table[row, col]) / (np.sum(table, axis=1)[row]))
    return probabilities


def convert_prior(table):
    """Helper function to transform prior matrix to log probabilities
    with smoothening"""
    probabilities = (table + 1e-5) / (np.sum(table) + (1e-5 * N_tags))
    return np.log(probabilities)


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred,
    where each line contains a POS tag as in UNIVERSAL_TAGS
    """
    # using viterbi pseudocode
    pos_data = read_data_train(train_file_name + '.txt')
    count_words, all_tags = (zip(*pos_data))
    all_tags = Counter(all_tags)

    prior, transition, emission = train_HMM(train_file_name)
    pos_data = read_data_test(test_file_name + '.txt')
    sent_inds = read_data_ind(test_file_name + '.ind')
    probs = np.zeros((len(pos_data), N_tags))

    transition[np.isinf(transition)] = 0.00001

    for i in sent_inds:
        for state in range(N_tags):  # insert values of all starting words
            if (UNIVERSAL_TAGS[state], pos_data[i]) in emission:
                probs[i, state] = prior[state] * emission[(UNIVERSAL_TAGS[state], pos_data[i])]
            else:
                probs[i, state] = prior[state] * 0.00001

    for i in range(1, len(pos_data)):
        prev_word = i - 1
        if i in sent_inds and pos_data[i] in count_words:
            continue
        for state1 in range(N_tags):
            x = 0
            for state2 in range(N_tags):
                if (UNIVERSAL_TAGS[state1], pos_data[i]) in emission:
                    x = max(x, probs[prev_word, state2] *
                            transition[state2, state1] *
                            emission[UNIVERSAL_TAGS[state1], pos_data[i]])
                else:
                    x = max(x, all_tags[UNIVERSAL_TAGS[state1]]/len(count_words)*
                            transition[state2, state1] * 0.0001)

            probs[i, state1] = x

    results = find_best_tags(probs)

    write_results(test_file_name + '.pred', results)


def find_best_tags(probs):
    result = []
    for column in range(0, probs.shape[0]):
        col = list(probs[column, :])
        max_val = col.index(max(col))
        max_state = UNIVERSAL_TAGS[max_val]
        result.append(max_state)
    return result


if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t
    # <test file>" E.g. python3 tagger.py -d data/train-public -t
    # data/test-public-small
    parameters = sys.argv

    train_file_name = parameters[parameters.index("-d") + 1]
    test_file_name = parameters[parameters.index("-t") + 1]

    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)
