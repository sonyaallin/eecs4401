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
                            - number of times tag_i seen at start of sentence/number of sentences

            - transition:   - A 2D-array of size (N_tags, N_tags)
                            - The (i,j)'th entry stores the log probablity of seeing the j'th tag given it is a transition coming from the i'th tag in UNIVERSAL_TAGS
                            - i.e. transition[i, j] = log P(tag_j|tag_i)
                            - num tag i followed by j / num of tag i (that are not last tag in sentence)

            - emission:     - A dictionary type containing tuples of (str, str) as keys
                            - Each key in the dictionary refers to a (TAG, WORD) pair
                            - The TAG must be an element of UNIVERSAL_TAGS, however the WORD can be anything that appears in the training data
                            - The value corresponding to the (TAG, WORD) key pair is the log probability of observing WORD given a TAG
                            - i.e. emission[(tag, word)] = log P(word|tag)
                            - If a particular (TAG, WORD) pair has never appeared in the training data, then the key (TAG, WORD) should not exist.
                            - for each word-tag pair: num of times WORD tagged as TAG / num of times tag appears in all sentences

    Hints: 1. Think about what should be done when you encounter those unseen emission entries during deccoding.
           2. You may find Python's builtin Counter object to be particularly useful 
    """

    pos_data = read_data_train(train_file_name + '.txt') # [(WORD, TAG),...]
    sent_inds = read_data_ind(train_file_name + '.ind') # [index1, index2, index3,...]
    num_sentences = len(sent_inds)

    # Create prior array
    tag_starts = [pos_data[i][1] for i in sent_inds]
    tag_start_count = Counter(tag_starts)

    prior = np.full(N_tags, 1e-5)
    for i in range(N_tags):
        prob = tag_start_count[UNIVERSAL_TAGS[i]]/num_sentences
        if prob != 0:
            prior[i] = math.log(prob)

    # Create transition matrix
    transition = np.full((N_tags, N_tags), 0)
    tag_occurs_wo_last = np.full(N_tags, 0)

    all_tags_array = [d[1] for d in pos_data]
    sentences = collect_sentences(all_tags_array, sent_inds)
    for i in range(N_tags):
        tag_i = UNIVERSAL_TAGS[i]
        for j in range(N_tags):
            tag_j = UNIVERSAL_TAGS[j]

            for s in sentences:
                pairs = list(break_into_pairs(s))
                for p in pairs:
                    if p == [tag_i, tag_j]:
                        transition[i][j] += 1
                        tag_occurs_wo_last[i] += 1
    transition = np.log(transition / tag_occurs_wo_last[:, None])

    # create emission dict
    emission = {}

    # sum occurrences of tags in sentences
    tag_occurs = np.full(N_tags, 1e-5)
    for i in range(N_tags):
        tag_i = UNIVERSAL_TAGS[i]
        for s in sentences:
            count = Counter(s)
            tag_occurs[i] += count[tag_i]

    for w, t in pos_data:
        if (t, w) not in emission:
            emission[(t, w)] = 1
        else:
            emission[(t, w)] += 1

    for t, w in emission.keys():
        idx = UNIVERSAL_TAGS.index(t)
        emission[(t, w)] = math.log(emission[(t, w)] / tag_occurs[idx])

    return prior, transition, emission


def break_into_pairs(lst):
    for i in range(0, len(lst)):
        yield lst[i:i+2]


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """
    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name + '.txt')
    sent_inds = read_data_ind(test_file_name + '.ind')
    sentences = collect_sentences(pos_data, sent_inds)

    results = []
    for s in sentences:
        results.extend(viterbi(s, prior, transition, emission))

    write_results(test_file_name + '.pred', results)


def collect_sentences(data, indexes):
    sentences = []
    start_idx = indexes[0]
    for i in indexes[1:]:
        sentences.append(data[start_idx:i])
        start_idx = i
    sentences.append(data[start_idx:len(data)])
    return sentences


def viterbi(observation, prior, transition, emission):
    prob_trellis = np.empty((N_tags, len(observation)))
    path_trellis = np.empty((N_tags, len(observation)), dtype=object)

    for i in range(N_tags):
        key = (UNIVERSAL_TAGS[i], observation[0])
        if key not in emission:
            emission[key] = math.log(1e-5)
        prob_trellis[i][0] = prior[i] + emission[key]
        path_trellis[i][0] = [UNIVERSAL_TAGS[i]]

    for i in range(1, len(observation)):
        for j in range(N_tags):
            key = (UNIVERSAL_TAGS[j], observation[i])
            if key not in emission:
                emission[key] = math.log(1e-5)
            x = np.argmax([prob_trellis[t][i-1] + transition[t][j] + emission[key] for t in range(N_tags)])
            prob_trellis[j][i] = prob_trellis[x][i-1] + transition[x][j] + emission[(UNIVERSAL_TAGS[j], observation[i])]
            path_trellis[j][i] = path_trellis[x][i-1].copy()
            path_trellis[j][i].append(UNIVERSAL_TAGS[j])

    row_idx = np.argmax(prob_trellis, axis=0)[-1]
    return path_trellis[row_idx][-1]

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
