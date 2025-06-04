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
                            - i.e. transition[i, j] = log P(tag_j|tag_i)"

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
    prior = [1e-10 for i in range(N_tags)]
    prior_count = Counter()

    transition = [[1e-10 for j in range(N_tags)] for i in range(N_tags)]
    transition_counter = Counter()
    from_counter = Counter()

    emission = {}
    word_counter = Counter()
    tag_counter = Counter()

    prev = None
    for i in range(len(pos_data)):
        # prior probability
        if i in sent_inds:
            prev = pos_data[i][1]
            prior_count.update([pos_data[i][1]])
        else:
            # transition probability
            transition_counter.update([prev + pos_data[i][1]])
            from_counter.update([prev])
            prev = pos_data[i][1]
        # emission probability
        word_counter.update([(pos_data[i][1], pos_data[i][0])])
        tag_counter.update([pos_data[i][1]])

    for word in word_counter:
        emission[word] = np.log(1e-10) if tag_counter[word[0]] == 0 else np.log(
            word_counter[word] / tag_counter[word[0]])

    for i in range(N_tags):
        from_total = from_counter[UNIVERSAL_TAGS[i]]
        for j in range(N_tags):
            trans_key = UNIVERSAL_TAGS[i] + UNIVERSAL_TAGS[j]
            transition[i][j] = transition_counter[trans_key] / from_total

    prior_total_cnt = sum(prior_count.values())
    for i, t in enumerate(UNIVERSAL_TAGS):
        if t in prior_count:
            prior[i] = prior_count[t] / prior_total_cnt

    return np.log(prior), np.log(transition), emission


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)
    pos_data = read_data_test(test_file_name + '.txt')
    sent_inds = read_data_ind(test_file_name + '.ind')

    results = []
    for i in range(len(sent_inds)):
        if i < len(sent_inds) - 1:
            prob_trellis, path_trellis = _viterbi_helper(pos_data[sent_inds[i]:sent_inds[i + 1]], prior, transition,
                                                         emission)
        else:
            prob_trellis, path_trellis = _viterbi_helper(pos_data[sent_inds[-1]:], prior, transition, emission)

        final_probs = [p[-1] for p in prob_trellis]
        max_prob = max(final_probs)
        index = final_probs.index(max_prob)

        results.extend(path_trellis[index][-1])

    write_results(test_file_name + '.pred', results)


def _viterbi_helper(observables, prior, transition, emission):
    prob_trellis = [[-24 for j in range(len(observables))] for i in range(N_tags)]
    path_trellis = [[[] for j in range(len(observables))] for i in range(N_tags)]

    # Determine trellis values for X1 for each starting sentences
    for s in range(N_tags):
        prob_trellis[s][0] = prior[s] + emission.get((UNIVERSAL_TAGS[s], observables[0]), np.log(1e-10))
        path_trellis[s][0] = [UNIVERSAL_TAGS[s]]

    # For X2-XT find each current state's most likely prior state x.
    for o in range(1, len(observables)):
        for s in range(N_tags):
            temp_max = float('-inf')
            max_tag = ''
            # x = argmax(x in prob_trellis[x][o - 1] * transition[x, s] * emission[s, o])
            for x in range(N_tags):
                temp = prob_trellis[x][o - 1] + transition[x, s] + emission.get((UNIVERSAL_TAGS[s], observables[o]),
                                                                                np.log(1e-10))
                if temp > temp_max:
                    temp_max = temp
                    max_tag = x

            prob_trellis[s][o] = temp_max
            path_trellis[s][o] = path_trellis[max_tag][o-1] + [UNIVERSAL_TAGS[s]]

    return prob_trellis, path_trellis


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

