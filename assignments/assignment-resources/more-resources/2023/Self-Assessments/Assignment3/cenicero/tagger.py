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

    seed = 1e-6

    # Initialize the variables
    prior_count = [0 for i in range(N_tags)]
    transition_count = [[0 for i in range(N_tags)] for j in range(N_tags)]
    transition_i_count = [0 for i in range(N_tags)]
    emission_count = {}
    emission_tag_count = Counter()
    for i in range(N_tags):
        emission_count[UNIVERSAL_TAGS[i]] = Counter()
    sent_inds.append(-1)
    next_sen_ind = sent_inds.pop(0)
    prev_tag = None
    all_priors = 0

    for i in range(len(pos_data)):
        word,tag = pos_data[i]
        # update emission
        emission_tag_count[tag] += 1
        emission_count[tag][word] += 1

        # update priors if necessary
        if i == next_sen_ind:
            prior_count[tag_to_index(tag)] += 1
            all_priors += 1
            next_sen_ind = sent_inds.pop(0)
            prev_tag = None

        # update transition within each sentence
        if prev_tag is not None:
            transition_i_count[tag_to_index(prev_tag)] += 1
            transition_count[tag_to_index(prev_tag)][tag_to_index(tag)] += 1
        prev_tag = tag

    # transform prior, transition, emission from counts to log of probabilities
    prior = np.asarray([seed for i in range(N_tags)])
    transition = np.asarray([[seed for i in range(N_tags)] for j in range(N_tags)])
    emission = {}
    for i in range(N_tags):
        prior[i] = np.log(prior_count[i] / all_priors)

    for i in range(N_tags):
        for j in range(N_tags):
            if transition_count[i][j] == 0:
                transition[i][j] = -np.inf
            else:
                transition[i][j] = np.log(transition_count[i][j] / transition_i_count[i])

    for tag in emission_count:
        for word in emission_count[tag]:
            emission[(tag,word)] = np.log((seed + emission_count[tag][word])/emission_tag_count[tag])

    return prior, transition, emission

def tag_to_index(tag):
    return UNIVERSAL_TAGS.index(tag)
    

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    ####################
    # STUDENT CODE HERE
    ####################
    results = []
    sent_inds.append(-1)
    next_sent_ind = sent_inds.pop(0)
    words = []
    for i in range(len(pos_data)):
        if next_sent_ind == i:
            best_path = viterbi(words,prior,transition,emission)
            results = results + [UNIVERSAL_TAGS[best_path[i]] for i in range(len(best_path))]
            words = []
            next_sent_ind = sent_inds.pop(0)
        words.append(pos_data[i])

    best_path = viterbi(words,prior,transition,emission)
    results = results + [UNIVERSAL_TAGS[best_path[i]] for i in range(len(best_path))]

    write_results(test_file_name+'.pred', results)


def viterbi(words, prior, transition, emission):
    if len(words) == 0:
        return []

    prob_trellis = [[0 for i in range(len(words))] for j in range(N_tags)] # Array of size N_tags x len(words)
    path_trellis = [[[] for i in range(len(words))] for j in range(N_tags)] # Array of size N_tags x len(words)
    ninf = -np.inf
    seed = 1e-6
    # compute probabilities of first word
    first_word = words[0]
    for s in range(N_tags):
        emission_s_o = emission[(UNIVERSAL_TAGS[s],first_word)] if tuple([UNIVERSAL_TAGS[s],first_word]) in emission else np.log(seed)
        prob_trellis[s][0] = prior[s] + emission_s_o
        path_trellis[s][0] = [s]
    # now compute for all other words
    for o in range(1,len(words)):
        curr_word = words[o]
        for s in range(N_tags):
            # find x that maximizes the probability of that tag being true
            emission_s_o = emission[(UNIVERSAL_TAGS[s],curr_word)] if tuple([UNIVERSAL_TAGS[s],curr_word]) in emission else np.log(seed)
            probabilities = [prob_trellis[x][o-1] + transition[x][s] + emission_s_o for x in range(N_tags)]
            x = np.argmax(probabilities)
            prob_trellis[s][o] = prob_trellis[x][o-1] + transition[x][s] + emission_s_o
            path_trellis[s][o] = path_trellis[x][o-1] + [s]

    # pick the best path
    best_tag = np.argmax([prob_trellis[s][len(words)-1] for s in range(N_tags)])
    best_path = path_trellis[best_tag][len(words)-1]
    return best_path
            



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