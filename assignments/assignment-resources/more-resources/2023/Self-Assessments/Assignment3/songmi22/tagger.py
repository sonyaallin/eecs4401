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

    tag_all = []
    for word in sent_inds:
        tag_all.append(pos_data[word][1])
    tag_sum = Counter(tag_all)
    total = 0
    for key in tag_sum.keys():
        total += tag_sum[key]
    i_pre = []
    for tag in UNIVERSAL_TAGS:
        i_pre.append(tag_sum[tag]/total)
    prior = np.log(i_pre)  

    transition = np.zeros(shape=(N_tags,N_tags))

    sentences = []
    tag_tracker = np.zeros(shape=(N_tags))
    pair_learner = {}

    for i in range(len(sent_inds) - 1):
        sentences.append(pos_data[sent_inds[i]:sent_inds[i+1]])
    sentences.append(pos_data[sent_inds[len(sent_inds)-1]:])

    for sentence in sentences:
        for i in range(len(sentence)-1):
            x_1 = sentence[i][1]
            x_2 = sentence[i+1][1]
            for j in range(N_tags):
                if UNIVERSAL_TAGS[j] == x_1:
                    tag_tracker[j] += 1
            if (x_1, x_2) in pair_learner.keys():
                pair_learner[(x_1, x_2)] += 1
            else:
                pair_learner[(x_1, x_2)] = 1

    for i in range(len(transition)):
        for j in range(len(transition)):
            if (UNIVERSAL_TAGS[i], UNIVERSAL_TAGS[j]) in pair_learner.keys():
                log_prob = np.log(pair_learner[UNIVERSAL_TAGS[i], UNIVERSAL_TAGS[j]] / tag_tracker[i])
                transition[i][j] = log_prob
            else:
                transition[i][j] = float('-inf')

    tag_tracker = {}
    emission = {}
    for sentence in sentences:
        for word in sentence:
            pair = (word[1], word[0])
            if word[1] in tag_tracker.keys():
                tag_tracker[word[1]] += 1
            else:
                tag_tracker[word[1]] = 1
            if pair in emission.keys():
                emission[pair] += 1
            else:
                emission[pair] = 1
    for key in emission.keys():
        ans = np.log(emission[key]/tag_tracker[key[0]])
        emission[key] = ans
    
    return prior, transition, emission

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    viterbi(O, S, Π, A, B):  
    prob_trellis = matrix(length(S), length(O))  
    path_trellis = matrix(length(S), length(O))
    # Determine trellis values for X1
    for s in range(length(S)):
    prob_trellis[s,0] = Π[s] * B[s, O[0]] 
    path_trellis[s,0] = [s]
    # For X2-XT find each current state's most likely prior state x.
    for o in range(1, length(O)):
    for s in range(length(S)):
    x = argmax(x in prob_trellis[x, o-1] * A[x,s] * B[s,o])
    prob_trellis[s,o] = prob_trellis[x, o-1] * A[x,s] * B[s,o]
    path_trellis[s,o] = path_trellis[x, o-1].append[s]
    return prob_trellis, path_trellis
    """

    prior, transition, emission = train_HMM(train_file_name)
    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    ####################
    # STUDENT CODE HERE
    ####################

    sentences = []
    results = []
    for i in range(len(sent_inds)-1):
        sentences.append(pos_data[sent_inds[i]:sent_inds[i+1]])
    sentences.append(pos_data[sent_inds[len(sent_inds)-1]:])
    
    for sentence in sentences:
        prob_trellis = np.zeros(shape = (N_tags, len(sentence)))
        path_trellis = np.zeros(shape = (N_tags, len(sentence)), dtype=object)
        for s in range(N_tags):        
            prob_trellis[s, 0] = prior[s] + emission.get((UNIVERSAL_TAGS[s], sentence[0]), np.log(1*10**-10))
            path_trellis[s, 0] = [s]
        for o in range(1, len(sentence)):
            for s in range(N_tags):
                x = np.argmax(prob_trellis[:, o-1] + transition[:, s]  + emission.get((UNIVERSAL_TAGS[s], sentence[o]), np.log(1*10**-10)))
                prob_trellis[s,o] = prob_trellis[x, o-1] + transition[x,s] + emission.get((UNIVERSAL_TAGS[s], sentence[o]), np.log(1*10**-10))
                path_trellis[s,o] = path_trellis[x, o-1] + [s]
        max_pred = np.argmax(prob_trellis[:, len(sentence)-1])
        path_max = path_trellis[max_pred][len(sentence)-1]
        pred_wrd = []
        for tag in path_max:
            pred_wrd.append(UNIVERSAL_TAGS[tag])
        results += pred_wrd
    write_results(test_file_name+'.pred', results)

if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = 'data/train-public'
    test_file_name = 'data/test-public-small'

    # Start the training and tagging operation.
    tag (train_file_name, test_file_name)