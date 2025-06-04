# The tagger.py starter code for CSC384 A4.

import os
import sys

import numpy as np
import math
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
            - file_name.txt: Each line contains a pair of word and its
                             Part-of-Speech (POS) tag
            - fila_name.ind: The i'th line contains an integer denoting the
                             starting index of the i'th sentence in the text-POS
                             data above

    Output: Three pieces of HMM parameters stored in LOG PROBABILITIES :

            - prior:        - An array of size N_tags
                            - Each entry corresponds to the prior log
                              probability of seeing the i'th tag in
                              UNIVERSAL_TAGS at the beginning of a sequence
                            - i.e. prior[i] = log P(tag_i)

            - transition:   - A 2D-array of size (N_tags, N_tags)
                            - The (i,j)'th entry stores the log probablity of
                              seeing the j'th tag given it is a transition
                              coming from the i'th tag in UNIVERSAL_TAGS
                            - i.e. transition[i, j] = log P(tag_j|tag_i)

            - emission:     - A dictionary type containing tuples of (str, str)
                              as keys
                            - Each key in the dictionary refers to a (TAG, WORD)
                              pair
                            - The TAG must be an element of UNIVERSAL_TAGS,
                              however the WORD can be anything that appears in
                              the training data
                            - The value corresponding to the (TAG, WORD) key
                              pair is the log probability of observing WORD
                              given a TAG
                            - i.e. emission[(tag, word)] = log P(word|tag)
                            - If a particular (TAG, WORD) pair has never
                              appeared in the training data, then the key (TAG,
                              WORD) should not exist.

    Hints: 1. Think about what should be done when you encounter those unseen
              emission entries during deccoding.
           2. You may find Python's builtin Counter object to be particularly
              useful
    """

    pos_data = read_data_train(train_file_name+'.txt')
    sent_inds = read_data_ind(train_file_name+'.ind')

    #####################
    # STUDENT CODE HERE #
    #####################

    num_seq = len(sent_inds)  # the number of sentences in the training set.

    # Deal with Prior Here
    prior = np.zeros(N_tags)  # initialize prior counters.
    for index in sent_inds:
        temp_tag = pos_data[index][1]
        if temp_tag in UNIVERSAL_TAGS:
            prior[UNIVERSAL_TAGS.index(temp_tag)] += 1
    prior = np.log(prior / sum(prior))

    # Deal With Transition Here
    transition = np.zeros((N_tags, N_tags))
    counts = {tag: 0 for tag in UNIVERSAL_TAGS}
    for i in range(len(sent_inds) - 1):
        sentence = pos_data[sent_inds[i]: sent_inds[i+1]]
        for t in range(len(sentence) - 1):
            word_t1, tag_t1 = sentence[t]
            word_t2, tag_t2 = sentence[t + 1]
            tag_t1_index = UNIVERSAL_TAGS.index(tag_t1)
            tag_t2_index = UNIVERSAL_TAGS.index(tag_t2)
            transition[tag_t1_index, tag_t2_index] += 1
            counts[tag_t1] += 1

    sentence = pos_data[sent_inds[-1]:]
    for t in range(len(sentence) - 1):
        word_t1, tag_t1 = sentence[t]
        word_t2, tag_t2 = sentence[t + 1]
        tag_t1_index = UNIVERSAL_TAGS.index(tag_t1)
        tag_t2_index = UNIVERSAL_TAGS.index(tag_t2)
        transition[tag_t1_index, tag_t2_index] += 1
        counts[tag_t1] += 1

    for tag in UNIVERSAL_TAGS:
        i = UNIVERSAL_TAGS.index(tag)
        count = counts[tag]
        transition[i] = transition[i] / count

    transition = np.log(transition)

    # Deal with Emission Here
    pairs = []
    tag2word = {tag: [] for tag in UNIVERSAL_TAGS}
    for pair in pos_data:
        word, tag = pair
        if tag in UNIVERSAL_TAGS:
            if pair not in pairs:
                pairs.append(pair)
            tag2word[tag].append(word)

    emission = {}

    for pair in pairs:
        w, t = pair  # extracting w word and t tag
        emission[(t, w)] = math.log(tag2word[t].count(w) / len(tag2word[t]))

    return prior, transition, emission


def viturbi(sen, p, t, e):
    """
    sen: sentence
    p: prior
    t: transition
    e: emission
    """
    prob_t = np.zeros((len(UNIVERSAL_TAGS), len(sen)))
    path_t = np.zeros((len(UNIVERSAL_TAGS), len(sen), len(sen)))

    for i in range(N_tags):
        prob = 0.00001
        tag = UNIVERSAL_TAGS[i]
        if (tag, sen[0]) in e.keys():
            prob = e[(tag, sen[0])]
        prob_t[i, 0] = p[i] * prob
        path_t[i, 0] = [i]

    for o in range(1, len(sen)):  # o is the index of the word in the sentence
        for i in range(N_tags):  # i represents the index of the tag observing
            # what we want to do is take the all of the optimal paths to the
            # previous word, and look at which one, when transitioning to this
            # word, would have the highest probability.
            curr_tag = UNIVERSAL_TAGS[i]
            king = ('', -np.inf)
            for j in range(N_tags):  # j is index of potntial prior
                prior_prob = prob_t[j, o - 1] + t[j, i] + e_prob(sen[o],
                                                                 curr_tag, e)
                if king[1] < prior_prob:
                    # We have a new most likely previous tag
                    king = (j, prior_prob)
            # king now refers to (j, p) where there is p probability j comes b4

            prob_t[i, o] = king[1]
            path_t[i, o] = path_t[i, o - 1]
            path_t[i, o, o] = king[0]

    return prob_t, path_t


def e_prob(e, tag, e_dict):
    """
    e: emission
    tag: potential tag
    e_dict: Dictionary mapping (tag, e) -> P(e|tag)

    return P(e|tag) if it exists, otherwise, return a very small probability
    """
    prob = 0.00001
    if (tag, e) in e_dict.keys():
        prob = e_dict[(tag, e)]
    return prob


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each
    line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    ####################
    # STUDENT CODE HERE
    ####################
    temp = []  # This should just be a list of tags.

    for i in range(len(sent_inds) - 1):
        sentence = pos_data[sent_inds[-1]:]
        prob_t, path_t = viturbi(sentence, prior, transition, emission)

        print(prob_t)

        print("____________________")

        print(path_t)

        paths = path_t[:, -1, :]
        print(paths)

        tags = paths[prob_t.argmax(axis=1)[-1]]

        temp.extend(tags)

    sentence = pos_data[sent_inds[-1]:]
    prob_t, path_t = viturbi(sentence, prior, transition, emission)

    print(prob_t)

    print("____________________")

    print(path_t)

    paths = path_t[:, -1, :]
    print(paths)

    tags = paths[prob_t.argmax(axis=1)[-1]]

    temp.extend(tags)

    # Emissions are atual words and X's are tags.

    results = []

    for item in temp:
        results.append(UNIVERSAL_TAGS[int(item)])

    write_results(test_file_name+'.pred', results)




"""

def viturbi(sentence, prior, tran, e):
    ""
    This function takes in a sentence, does recursive processing using the
    viturbi algorithm, then returns a list of tag paths associated with a prob.

    return looks like tuple(list, float) where there is float prob list is tags
    ""

    final = ([], 0.0)

    if len(sentence) == 0:  # We shouldnt really be getting to this position
        return []

    if len(sentence) == 1:  # This is the real base case, we are looking at the
        # first word in a sentence.
        word = sentence[0]
        p_dict = {}  # This will contain probability data for this word
        king = ('', 0.0)
        for tag in UNIVERSAL_TAGS:
            if (tag, word) in prior.keys():
                p_dict[tag] = e[(tag, word)] * prior[UNIVERSAL_TAGS.index(tag)]
            else:
                p_dict[tag] = 0.00001 * prior[UNIVERSAL_TAGS.index(tag)]
            if p_dict[tag][1] > king[1]:
                king = p_dict[tag]
        return [king]

    tags_so_far = viturbi(sentence[:-1], prior, tran, e)
    e_t, x_tless = sentence[-1], tags_so_far[0][-1]

    for tag in UNIVERSAL_TAGS:
        temp_list, temp_prob = tags_so_far + [tag], 0

        # 

        pot_final =

    return final
"""

if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # TaggerExpectsInputCall: "python3 tagger.py -d <train file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d")+1]
    test_file_name = parameters[parameters.index("-t")+1]

    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)
