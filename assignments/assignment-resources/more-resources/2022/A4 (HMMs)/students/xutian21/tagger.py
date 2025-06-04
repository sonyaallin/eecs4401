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

    tags = [word[1] for word in pos_data]
    start_tags = [tags[ind] for ind in sent_inds]
    tag_counter = Counter()
    tag_counter.update(start_tags)
    # tags in the start of sentence
    start_tag_counts = [tag_counter[t] for t in UNIVERSAL_TAGS]
    # compute prior
    prior = np.log(np.array(start_tag_counts) / len(sent_inds))
    # (tag, word) counts
    emission_counter = Counter()
    emission_counter.update(pos_data)
    # tag counts
    tag_counter = Counter()
    tag_counter.update(tags)

    # compute emission
    emission = {}
    for (w, t) in emission_counter:
        emission[(t, w)] = np.log(emission_counter[(w, t)] / tag_counter[t])
    end_inds = sent_inds[1:] + [len(pos_data)]
    trans_counter = Counter()
    # for each sentence
    for start_ind, end_ind in zip(sent_inds, end_inds):
        pairs = [ (tags[i], tags[i+1]) for i in range(start_ind, end_ind - 1)]
        pre = [x for x, _ in pairs]
        # update (tag1, tag2) pair counts
        trans_counter.update(pairs)
        # update tag count
        trans_counter.update(pre)

    # compute transition matrix
    transition = np.zeros((N_tags, N_tags), dtype = float)
    for i in range(N_tags):
        for j in range(N_tags):
            x, y = UNIVERSAL_TAGS[i], UNIVERSAL_TAGS[j]
            if trans_counter[(x, y)] == 0:
                transition[i, j] = -float('inf')
            else:
                transition[i, j] =  np.log(trans_counter[(x, y)] / trans_counter[x])
    return prior, transition, emission

# return emission log(p(w | tag))
def getEmission(tag_id, w, emission):
    # small probability close to 0
    small_prob = np.log(1e-6)
    tag = UNIVERSAL_TAGS[tag_id]
    p = (tag, w)
    if p in emission:
        res = emission[p]
    else:
        res = small_prob
    return res

# tag one sentence using Viterbi algorithm
def tagOneSentance(words, prior, transition, emission):
    n = len(words)
    # optimal log probability
    opt = np.zeros((n, N_tags))
    # tag chosen
    choice = np.zeros((n, N_tags), dtype=int)
    # compute for start probability
    opt[0, :] = prior + [getEmission(i, words[0], emission) for i in range(N_tags)]

    # for each sentence length
    for i in range(1, n):
        # for each tag
        for s in range(N_tags):
            vs = [transition[pre, s] + opt[i - 1, pre] for pre in range(N_tags)]
            # find max one
            max_pre = np.argmax(vs)
            max_v = vs[max_pre]

            choice[i, s] = max_pre
            opt[i, s] = max_v + getEmission(s, words[i], emission)
    # compute sequence result
    max_sq = [0] * n
    xt = np.argmax(opt[n - 1])
    for i in range(n - 1, -1, -1):
        max_sq[i] = xt
        xt = choice[i, xt]

    return max_sq

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
    end_inds = sent_inds[1:] + [len(pos_data)]

    # for each sentence
    for start_ind, end_ind in zip(sent_inds, end_inds):
        words = pos_data[start_ind:end_ind]
        # tag the sentence
        tag_ids = tagOneSentance(words, prior, transition, emission)
        tag_str = [UNIVERSAL_TAGS[i] for i in tag_ids]

        results.extend(tag_str)

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
