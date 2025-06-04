# The tagger.py starter code for CSC384 A4.
import os
import sys
import random

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
# numbers of tag
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
    # ------ Do prior ------ #
    prior = []
    num_tags_train = [0 for i in range(N_tags)]
    num_sentences = len(sent_inds)
    for index in sent_inds:
        start_word, word_tag = pos_data[index]
        num_tags_train[UNIVERSAL_TAGS.index(word_tag)] += 1
    # print(sum(num_tags_train))
    for number in num_tags_train:
        prior.append(np.log(number / num_sentences))

    # print(prior)

    # ------ Do transition ------ #
    transition = [[0 for _ in range(N_tags)] for _ in range(N_tags)]

    num_tag_appear = [0 for _ in range(N_tags)]
    trans_appear = [[0 for _ in range(N_tags)] for _ in range(N_tags)]
    trans_pos = [[0 for _ in range(N_tags)] for _ in range(N_tags)]
    n_words = len(pos_data)

    sentence_index = 1
    s2 = 0
    for tu_i in range(len(pos_data) - 1):

        w, word_tag = pos_data[tu_i]
        correspond_index_tag = UNIVERSAL_TAGS.index(word_tag)

        # for transition
        next_tag = pos_data[tu_i + 1][1]  # VERIFIED
        correspond_next = UNIVERSAL_TAGS.index(next_tag)

        # number of transition appear in the dictionary
        if sentence_index < num_sentences:
            s2 += 1
            if tu_i + 1 == sent_inds[sentence_index]:  # Removed . -> word2
                sentence_index += 1

            else:
                trans_appear[correspond_index_tag][correspond_next] += 1
                num_tag_appear[correspond_index_tag] += 1  # VERIFIED
        else:
            trans_appear[correspond_index_tag][correspond_next] += 1
            num_tag_appear[correspond_index_tag] += 1  # VERIFIED

    for i in range(N_tags):
        for j in range(N_tags):
            if trans_appear[i][j] == 0:
                transition[i][j] = float('-inf')
            else:
                transition[i][j] = np.log(
                    trans_appear[i][j] / num_tag_appear[i])

    # ------ emission ------ #
    emission = {}
    # 1. get Dict{tag: [words]}, Dict{word: [tag]}, {(tag, word): times}

    tag_dict = {}
    t_w_times = {}

    for w, word_tag in pos_data:
        if tag_dict.get(word_tag) is None:
            tag_dict[word_tag] = 1
        else:
            tag_dict[word_tag] += 1

        tmp_tu = word_tag, w
        if tmp_tu not in t_w_times:
            t_w_times[tmp_tu] = 1
        else:
            t_w_times[tmp_tu] += 1

    # 2. P(word n tag) and P(tag)

    for t_w_tu, num in t_w_times.items():
        tu_tag, tu_word = t_w_tu
        # P(word n tag)
        p_w_n_tag = num
        p_tag = tag_dict[tu_tag]
        emission[t_w_tu] = np.log(p_w_n_tag / p_tag)

    prior = np.array(prior)
    transition = np.array(transition)
    # emission = np.array(emission)
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
    # print('In the tag------------------------------------------')
    # print(pos_data)
    results = []
    for word in pos_data:
        pos_lst = []
        for w_tag in UNIVERSAL_TAGS:
            temp_tu = (w_tag, word)
            if emission.get(temp_tu) is not None:
                pos_lst.append((temp_tu, abs(emission[temp_tu])))
        pos_lst.sort(key=lambda tu: tu[1])
        pos_lst.reverse()
        if pos_lst:
            # print(pos_lst[0][0][0], '??????')

            results.append(pos_lst[0][0][0])

        else:
            results.append('NOUN')

    write_results(test_file_name+'.pred', results)

    return results


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
