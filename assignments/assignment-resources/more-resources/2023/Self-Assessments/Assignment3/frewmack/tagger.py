# The tagger.py starter code for CSC384 A4.

from enum import unique
import os
import sys

import numpy as np
import numpy.ma as ma

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
almost_zero = 1e-5

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
                            - Each entry corresponds to the prior log probability of seeing the i'th tag in UNIVERSAL_TAGS at the __beginning__ of a sequence
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

    # dictionary mapping a tag to its index in UNIVERSAL_TAGS
    tags = dict(map(lambda x: (x[1], x[0]), enumerate(UNIVERSAL_TAGS)))

    unique_words = set()
    for word, _ in pos_data:
        unique_words.add(word)

    unique_words = list(unique_words)
    words_indexed = dict(map(lambda x: (x[1], x[0]), enumerate(unique_words)))

    # counters
    prior_count = np.zeros((N_tags,))
    transition_count = np.zeros((N_tags, N_tags))
    emission_count = np.zeros((N_tags, len(unique_words)))
    tag_count = np.zeros((N_tags,))
    prev_tag_count = np.zeros((N_tags,))

    num_inds = len(sent_inds)
    data_len = len(pos_data)

    curr_ind_idx = 0
    curr_seq_idx = sent_inds[curr_ind_idx]
    previous_tag = None
    for i, wordtag in enumerate(pos_data):
        word, tag = wordtag
        if i == curr_seq_idx:
            prior_count[tags[tag]] += 1
            curr_ind_idx += 1
            if curr_ind_idx < num_inds:
                curr_seq_idx = sent_inds[curr_ind_idx]
            else:
                curr_seq_idx = data_len
        else:
            transition_count[tags[previous_tag], tags[tag]] += 1

        emission_count[tags[tag], words_indexed[word]] += 1
        tag_count[tags[tag]] += 1
        if i < data_len-1 and i != curr_seq_idx - 1:
            # exclude the last tag from this count, since it's only used for calculating transition
            # (the last tag in the data can never be a "previous tag")
            prev_tag_count[tags[tag]] += 1
        previous_tag = tag

    # we have counts; now we need to calculate log probabilities
    prior = np.log(prior_count / np.sum(prior_count))
    # P(A|B) = P(A, B) / P(B)
    # use masked array operations to avoid divide by zero, then set the expected -np.inf afterwards
    transition_count = ma.masked_array(transition_count, mask=(transition_count == 0))
    transition = ma.log(transition_count / prev_tag_count.reshape((N_tags, 1)))
    transition[transition.mask] = -np.inf
    transition.mask = False


    # for emissions, we want to convert to an N x D array to calculate log p(word|tag), then convert back to dictionary
    # since numpy can do these operations faster than we can
    # (D := num of unique words)
    emission_count = ma.masked_array(emission_count, mask=(emission_count == 0))
    emission_array = ma.log(emission_count / tag_count.reshape((N_tags, 1)))  # N x D
    emission = dict()

    # convert back to dictionary (likely a bottleneck)
    for i, tag_row in enumerate(emission_array):
        for j, word_prob in enumerate(tag_row):
            if word_prob is not ma.masked:
                emission[(UNIVERSAL_TAGS[i], unique_words[j])] = word_prob

    return prior, transition, emission


def viterbi(observations, prior, transition, emission):
    # based on pseudocode from lecture
    # all probabilities are log probabilities, so we can add instead of multiplying
    # whether they're "true" probabilities or not doesn't really matter since we just take the max

    observe_len = len(observations)
    prob_trellis = np.ndarray((N_tags, observe_len))

    for s in range(N_tags):
        prob_trellis[s, 0] = prior[s] + emission.get((UNIVERSAL_TAGS[s], observations[0]), np.log(1e-5))

    for o in range(1, observe_len):
        for s in range(N_tags):
            x = np.argmax(prob_trellis[:, o-1] + transition[:, s] + emission.get((UNIVERSAL_TAGS[s], observations[o]), np.log(1e-5)))
            prob_trellis[s,o] = prob_trellis[x, o-1] + transition[x, s] + emission.get((UNIVERSAL_TAGS[s], observations[o]), np.log(1e-5))

    return prob_trellis


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    # we need to account for -np.inf popping up because of divides by zero
    # we don't fix it in train_HMM because otherwise the autograder fails .-.

    pos_data = np.array(pos_data)
    sent_inds = np.array(sent_inds)

    results = []

    for observations in np.split(pos_data, sent_inds):
        n = np.shape(observations)[0]
        if n == 0:
            continue

        prob_trellis = viterbi(observations, prior, transition, emission)
        most_likely_tags = list(prob_trellis.argmax(axis=0))
        predictions = [UNIVERSAL_TAGS[x] for x in most_likely_tags]

        results.extend(predictions)


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
    tag (train_file_name, test_file_name)