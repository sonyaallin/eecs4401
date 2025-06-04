# The tagger.py starter code for CSC384 A4.
import os
import sys

import math
from matplotlib import path
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

TINY_NUMBER = 0.00000000000000000001

N_tags = len(UNIVERSAL_TAGS)

# Removes the runtime warning...
np.seterr(divide='ignore')

def read_data_train(path):
    return [
        tuple(line.split(" : ")) for line in open(path, "r").read().split("\n")[:-1]
    ]


def read_data_test(path):
    return open(path, "r").read().split("\n")[:-1]


def read_data_ind(path):
    return [int(line) for line in open(path, "r").read().split("\n")[:-1]]


def write_results(path, results):
    with open(path, "w") as f:
        f.write("\n".join(results))


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

    pos_data = read_data_train(train_file_name + ".txt")
    sent_inds = read_data_ind(train_file_name + ".ind")

    # Gather the prior probabilities
    cnt = Counter()
    prior = []
    for index in sent_inds:
        cnt[pos_data[index][1]] += 1
    total_start = sum(cnt.values())

    # Append in the order given with universal tags
    for item in UNIVERSAL_TAGS:
        # if cnt[item] == 0:
        #     # prior.append(TINY_NUMBER)
        #     prior.append(0)
        # else:
        prior.append(cnt[item] / total_start)

    prior = np.log(np.array(prior))

    # Gather the transition probabilities
    cnt = Counter()
    cnt_starting = Counter()
    for j in range(len(sent_inds)):
        starting_index = sent_inds[j]
        if j == len(sent_inds) - 1:
            ending_index = len(pos_data)
        else:
            ending_index = sent_inds[j + 1]
        for i in range(ending_index - starting_index - 1):
            k = i + starting_index
            cnt[(pos_data[k][1], pos_data[k + 1][1])] += 1
            cnt_starting[pos_data[k][1]] += 1

    # Get the total number of transitions within the data
    # Create the Transition Probability Table
    transition = []
    for idx1 in UNIVERSAL_TAGS:
        inner = []
        for idx2 in UNIVERSAL_TAGS:
            value = cnt[(idx1, idx2)]
            if value == 0:
                # inner.append(TINY_NUMBER)
                inner.append(cnt[(idx1, idx2)])
            else:
                if cnt_starting[(idx1)] != 0:
                    inner.append(cnt[(idx1, idx2)] / cnt_starting[(idx1)])
                else:
                    inner.append(cnt[(idx1, idx2)])
        transition.append(inner)

    transition = np.log(np.array(transition))

    # Gather emission probabilities
    emission = Counter()
    tag_count = Counter()
    for item in pos_data:
        emission[(item[1], item[0])] += 1
        tag_count[(item[1])] += 1

    for k in emission.keys():
        emission[k] = math.log(emission[k] / tag_count[k[0]])

    # print(emission)
    return prior, transition, emission


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """
    results = []
    prior, transition, emission = train_HMM(train_file_name)
    pos_data = read_data_test(test_file_name + ".txt")
    sent_inds = read_data_ind(test_file_name + ".ind")

    # Iterate over sentences
    for j in range(len(sent_inds)):
        starting_index = sent_inds[j]
        if j == len(sent_inds) - 1:
            ending_index = len(pos_data)
        else:
            ending_index = sent_inds[j + 1]

        # Viterbi Algorithm
        sent_length = ending_index - starting_index
        prob_trellis = np.zeros((len(UNIVERSAL_TAGS), sent_length))
        path_trellis = np.empty((len(UNIVERSAL_TAGS), sent_length), dtype=object)

        for tag in range(len(UNIVERSAL_TAGS)):
            if (UNIVERSAL_TAGS[tag], pos_data[starting_index]) in emission.keys():
                prob_trellis[tag, 0] = (
                    prior[tag]
                    + emission[(UNIVERSAL_TAGS[tag], pos_data[starting_index])]
                )
            else:
                prob_trellis[tag, 0] = prior[tag] + math.log(TINY_NUMBER)
            path_trellis[tag, 0] = [UNIVERSAL_TAGS[tag]]

        for idx in range(1, sent_length):
            k = idx + starting_index
            for tag in range(len(UNIVERSAL_TAGS)):
                if (UNIVERSAL_TAGS[tag], pos_data[k]) in emission.keys():
                    x = np.argmax(
                        prob_trellis[:, idx - 1]
                        + transition[:, tag]
                        + emission[(UNIVERSAL_TAGS[tag], pos_data[k])]
                    )
                    prob_trellis[tag, idx] = (
                        prob_trellis[x, idx - 1]
                        + transition[x, tag]
                        + emission[(UNIVERSAL_TAGS[tag], pos_data[k])]
                    )
                else:  # If you can't find it, then add a tiny number
                    x = np.argmax(
                        prob_trellis[:, idx - 1]
                        + transition[:, tag]
                        + math.log(TINY_NUMBER)
                    )
                    prob_trellis[tag, idx] = (
                        prob_trellis[x, idx - 1]
                        + transition[x, tag]
                        + math.log(TINY_NUMBER)
                    )
                # Update the Sequence
                path_trellis[tag, idx] = path_trellis[x, idx - 1][:]
                path_trellis[tag, idx].append(UNIVERSAL_TAGS[tag])

        x = np.argmax(prob_trellis[:, sent_length - 1])
        results += path_trellis[x, sent_length - 1]

    write_results(test_file_name + ".pred", results)


if __name__ == "__main__":
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d") + 1]
    test_file_name = parameters[parameters.index("-t") + 1]

    # train_HMM("train-public")
    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)

