# The tagger.py starter code for CSC384 A4.

import os
import sys

import numpy as np
from collections import Counter



UNIVERSAL_TAGS = [
    "VERB", #0
    "NOUN", #1
    "PRON", #2
    "ADJ", #3
    "ADV", #4
    "ADP", #5
    "CONJ", #6
    "DET", #7
    "NUM", #8
    "PRT", #9
    "X", #10
    ".", #11
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
                            - i.e. prior[i] = log P(tag_i )

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
    htable = {}
    for tag in UNIVERSAL_TAGS:
        htable[tag] = 0
    transition_dict = {}
    for tag in UNIVERSAL_TAGS:
        transition_dict[tag] = htable.copy()
    for num in sent_inds:
        tag = pos_data[num][1]
        htable[tag] += 1
    total = sum(htable.values())
    for tag in htable.keys():
        htable[tag] = np.log(htable[tag] / total)
    index = 1
    for i, j in zip(range(0, len(pos_data) - 1), range(1, len(pos_data))):
        if index < len(sent_inds):
            start = sent_inds[index]
        before = pos_data[i][1]
        after = pos_data[j][1]
        if j != start:
            transition_dict[before][after] += 1
        else:
            index += 1
    for tag in transition_dict:
        total = sum(transition_dict[tag].values())
        for follow in transition_dict[tag].keys():
            if transition_dict[tag][follow] != 0:
                transition_dict[tag][follow] = transition_dict[tag][follow]/total
                transition_dict[tag][follow] = np.log(transition_dict[tag][follow])
            else:
                transition_dict[tag][follow] = float("-inf")
    htable2 = {}
    for tag in UNIVERSAL_TAGS:
        htable2[tag] = 0
    for word in pos_data:
        htable2[word[1]] += 1
    for i in range(len(pos_data)):
        left, right = pos_data[i][0], pos_data[i][1]
        data = (right, left)
        pos_data[i] = data
    emission = Counter(pos_data)
    for word in emission.keys():
        emission[word] = np.log(emission[word]/htable2[word[0]])
    prior = np.array(list(htable.values()))
    transition = np.zeros(shape=(N_tags, N_tags))
    for i in range(len(transition_dict)):
        for j in range(len(transition_dict[UNIVERSAL_TAGS[i]])):
            transition[i][j] = transition_dict[UNIVERSAL_TAGS[i]][UNIVERSAL_TAGS[j]]

    return prior, transition, emission
    

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
    #initial

    results = []
    previous = sent_inds[0]
    for i in range(1, len(sent_inds) + 1):
        if i != len(sent_inds):
            sentence = pos_data[previous:sent_inds[i]]
            previous = sent_inds[i]
        else:
            sentence = pos_data[previous:]
        probs, paths = viterbi(UNIVERSAL_TAGS, sentence, prior, transition, emission)
        best = np.where(probs[:,len(sentence)-1] == max(probs[:,len(sentence)-1]))[0]
        results += (paths[best, len(sentence)-1][0])
    for i in range(len(results)):
        results[i] = UNIVERSAL_TAGS[results[i]]

    soln = read_data_soln('data/test-public-small.soln')
    cor = 0
    total = 0
    for pred, actual in zip(results, soln):
        if pred == actual:
            cor += 1
        total += 1

    write_results(test_file_name+'.pred', results)

    #python tagger.py -d data/train-public -t data/test-public-small

def viterbi(tags, observations, prior, transition, emission):
    np.set_printoptions(suppress=True)
    prtrellis = np.zeros((len(tags), len(observations)))
    patrellis = np.zeros((len(tags), len(observations)), dtype=object)
    for s in range(len(tags)):
        emi2 = emission[UNIVERSAL_TAGS[s], observations[0]]
        if emi2 == 0:
            emi2 = 0.000001
        prtrellis[s, 0] = prior[s] * emi2
        patrellis[s, 0] = [s]
    for o in range(1, len(observations)):
        for t in range(len(tags)):
            emi = emission[UNIVERSAL_TAGS[t], observations[o]]
            if emi == 0:
                emi = 0.000001
            max, max_tag = maxprob(prtrellis, transition, o, t)
            prtrellis[t, o] = max * -emi
            patrellis[t, o] = patrellis[max_tag, o-1].copy()
            patrellis[t, o].append(t)
    return prtrellis, patrellis

def maxprob(prt, trans, obs, tag):
    max = float("-inf")
    max_tag = None
    for t in range(len(UNIVERSAL_TAGS)):
        if trans[t, tag] == float("-inf"):
            calc = prt[t, obs-1] * 0.000001
        else:
            calc = np.exp(np.logaddexp(prt[t, obs-1], trans[t, tag]))
        if calc > max:
            max = calc
            max_tag = t
    return max, max_tag


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