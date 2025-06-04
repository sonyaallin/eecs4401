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

# Easier Indexing
TAG_INDEXES = {
    "VERB": 0,
    "NOUN": 1,
    "PRON": 2,
    "ADJ": 3,
    "ADV": 4,
    "ADP": 5,
    "CONJ": 6,
    "DET": 7,
    "NUM": 8,
    "PRT": 9,
    "X": 10,
    ".": 11,
}

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
    tag_ctr = Counter()
    for start_i in sent_inds:
        word, tag = pos_data[start_i]
        tag_ctr[tag] += 1

    n = len(sent_inds) # total number of sequences
    prior = np.zeros(N_tags)
    for i in range(N_tags):
        prob = tag_ctr[UNIVERSAL_TAGS[i]] / n
        log_p = np.log(prob)
        prior[i] = log_p

    transition = np.zeros((N_tags, N_tags))
    for idx in range(n):
        if idx == n - 1:
            start_idx, end_idx = sent_inds[idx], len(pos_data)
        else:
            start_idx, end_idx = sent_inds[idx], sent_inds[idx+1]

        for i in range(start_idx, end_idx):
            if i == start_idx:
                continue

            # The (i,j)'th entry stores the log probablity of seeing the j'th tag
            # given it is a transition coming from the i'th tag in UNIVERSAL_TAGS
            # i.e. transition[i, j] = log P(tag_j|tag_i)
            word_i, tag_i = pos_data[i-1]
            word_j, tag_j = pos_data[i]

            transition[TAG_INDEXES[tag_i], TAG_INDEXES[tag_j]] += 1

    transition /= np.sum(transition, keepdims=True, axis=1)
    transition = np.log(transition)

    #- emission:     - A dictionary type containing tuples of (str, str) as keys
    #                - Each key in the dictionary refers to a (TAG, WORD) pair
    #                - The TAG must be an element of UNIVERSAL_TAGS, however the WORD can be anything that appears in the training data
    #                - The value corresponding to the (TAG, WORD) key pair is the log probability of observing WORD given a TAG
    #                - i.e. emission[(tag, word)] = log P(word|tag)
    #                - If a particular (TAG, WORD) pair has never appeared in the training data, then the key (TAG, WORD) should not exist.

    all_words = list(set([word for word, tag in pos_data]))
    word_indexes = {}
    for i, word in enumerate(all_words):
        word_indexes[word] = i

    N_words = len(all_words)

    # emission_matrix[tag, word] = log P(word|tag)
    # calculated similarly to transition matrix
    emission_matrix = np.zeros((N_tags, N_words))

    for word, tag in pos_data:
        if tag not in UNIVERSAL_TAGS:
            break

        emission_matrix[TAG_INDEXES[tag], word_indexes[word]] += 1

    emission_matrix /= np.sum(emission_matrix, keepdims=True, axis=1)
    emission_matrix = np.log(emission_matrix)

    emission = {}
    for i in range(N_tags):
        for j in range(N_words):
            log_p = emission_matrix[i][j]

            # some WORDS are never observed given a TAG, resulting in log_p
            # of -inf, we don't include those in our emission dict
            if log_p != -float('inf'):
                tag = UNIVERSAL_TAGS[i]
                word = all_words[j]
                emission[(tag, word)] = emission_matrix[i, j]

    return prior, transition, emission

def viterbi(obs, states, initial_probs, trans_matrix, emission_dict):
    prob_trellis = np.zeros((len(states), len(obs)))
    path_trellis = np.ndarray((len(states), len(obs)), dtype=object)

    for i, s in enumerate(states):
        emission_dict[(s, obs[0])] = emission_dict.get((s, obs[0]), -15)
        prob_trellis[i, 0] = initial_probs[i] + emission_dict[(s, obs[0])]

    for o in range(1, len(obs)):
        for i, s in enumerate(states):
            emission_dict[(s, obs[o])] = emission_dict.get((s, obs[o]), -15)
            # Adding log probabilities instead of multiplying (log(A) + log(B) = log(A*B) in (-inf, 0] i.e. closer to 0, likelier))

            # obtain index of state with maximum likelihood up till this current state o
            max_idx = np.argmax([prob_trellis[idx, o-1] + trans_matrix[idx, i] + emission_dict[(s, obs[o])] for idx in range(N_tags)])
            # max_idx = np.argmax([prob_trellis[idx, o-1] + trans_matrix[idx, i] for idx in range(N_tags)])

            prob_trellis[i, o] = prob_trellis[max_idx, o-1] + trans_matrix[max_idx, i] + emission_dict[(s, obs[o])]
            
            # Assign max idx along path trellis w.r.t. current observation
            path_trellis[i, o] = max_idx

    # Backtrack along path trellis to obtain the best path (path with highest likelihood)
    best_path = []
    max_state_idx = np.argmax(prob_trellis[:,-1])
    for o in range(len(obs)-1, -1, -1):
        best_path.insert(0, UNIVERSAL_TAGS[max_state_idx])
        max_state_idx = path_trellis[max_state_idx, o]

    return best_path

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    # Prior (len: N_tags): Probability of seeing the ith universal tag at beginning of sequence
    # Transition (N_tags x N_tags): prob of seeing tag_j given tag_i before i.e. transition[i, j] = log P(tag_j|tag_i)
    # Emission (len: num unique (tag, word) pairs): d[(TAG, WORD)] = P(WORD | TAG)
    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    ####################
    # STUDENT CODE HERE
    ####################

    results = []

    n = len(sent_inds)
    for idx in range(n):
        if idx == n - 1:
            start_idx, end_idx = sent_inds[idx], len(pos_data)
        else:
            start_idx, end_idx = sent_inds[idx], sent_inds[idx+1]

        obs = pos_data[start_idx: end_idx]

        # We obtain the best_path for EACH SENTENCE
        best_path = viterbi(obs, UNIVERSAL_TAGS, prior, transition, emission)

        # tack best path for this sentence onto result
        results += best_path



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