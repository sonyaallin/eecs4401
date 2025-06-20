# The tagger.py starter code for CSC384 A4.

import os
import sys

import numpy as np
from collections import Counter, defaultdict

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

    starts = set(sent_inds)     # set of sentence starting indices
    sentences = max(len(starts), 1) # number of sentences

    count = defaultdict(int)    # count of each tag instance
    first = defaultdict(int)    # count of each prior tag instane
    trans = defaultdict(int)    # count of each transition pair
    pair = defaultdict(int)     # count of each emission pair

    prev = False
    for i, (word, tag) in enumerate(pos_data):
        if i in starts:         # increment count of prior tag
            first[tag] += 1
        if prev and i not in starts:    # increment count of transition that is in the same sentence
            trans[(prev, tag)] += 1
        prev = tag
        count[tag] += 1
        pair[(tag, word)] += 1

    np.seterr(divide='ignore')  # suppress division warning

    # convert count dictionaries to proper data structures with probabilities
    prior = np.array([first.get(tag, 1e-10)/sentences for tag in UNIVERSAL_TAGS])
    transition = np.array([[trans.get((tag_i, tag_j), 0.0) for tag_j in UNIVERSAL_TAGS] for tag_i in UNIVERSAL_TAGS])
    denominator = transition.sum(axis=1, keepdims=True)    # divide by row sum
    np.divide(transition, denominator, transition, where=denominator!=0)    # bayes rule
    emission = {k: np.log(v/max(count.get(k[0], 1), 1)) for k, v in pair.items()}   # bayes rule

    return np.log(prior), np.log(transition), emission
    

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

    sentences = len(sent_inds)
    end = len(pos_data)
    for i in range(sentences):    # group viterbi observations by sentences
        start = sent_inds[i]
        stop = sent_inds[i + 1] if i + 1 < sentences else end

        # viterbi algorithm from class; tags, prior, transition, emission already in outer scope
        def viterbi(words):
            tags = UNIVERSAL_TAGS
            O = len(words)  # observations
            S = len(tags)   # hidden states

            prob = np.zeros([S, O])
            path = np.empty([S, O], dtype=object)
            
            for s in range(S):    # initial trellis values
                prob[s,0] = prior[s] + emission.setdefault((tags[s], words[0]), np.log(1e-10))
                path[s,0] = [tags[s]]
            for o in range(1, O):    # find most probable prior state from current
                for s in range(S):
                    x = np.argmax(prob[:, o-1] + transition[:, s])    # Emission is constant so not needed
                    prob[s,o] = prob[x, o-1] + transition[x,s] + emission.setdefault((tags[s], words[o]), np.log(1e-10))
                    path[s,o] = path[x, o-1] + [tags[s]]
            return prob, path

        prob, path = viterbi(pos_data[start:stop])
        results.extend(path[np.argmax(prob[:, -1])][-1])    # select most probable tag
    
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