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

def compute_prior(data, ind):
    counts = Counter(np.asarray(data)[ind][:,1])    
    with np.errstate(divide='ignore'):
        return np.asarray([np.log(counts[tag]) - np.log(len(ind)) for tag in UNIVERSAL_TAGS])

def compute_transition(data, ind):
    counts_trans = Counter()
    counts_start = Counter()
    for i in range(len(ind)):
        start = ind[i]
        if i == len(ind)-1:
            end = len(data)
        else:
            end = ind[i+1]
        #print(f'{ind}: {data[start:end][1]}')
        #input()
        counts_trans += Counter([(data[j][1], data[j+1][1]) for j in range(start, end-1)])
        counts_start += Counter([data[j][1] for j in range(start, end-1)])
    with np.errstate(divide='ignore'):
        return np.asarray([[np.log(counts_trans[(tag1, tag2)]) - np.log(counts_start[tag1]) for tag2 in UNIVERSAL_TAGS] for tag1 in UNIVERSAL_TAGS])

def compute_emission(data, ind):
    counts_tags = Counter(np.asarray(data)[:,1])
    counts_words = Counter(data)
    return {(key[1], key[0]):np.log(counts_words[key]) - np.log(counts_tags[key[1]]) for key in counts_words}

epsilon = 1e-5
def lookup_emission(word, emission):
    w_emission = np.zeros(N_tags) - np.inf
    for i in range(N_tags):
        if (UNIVERSAL_TAGS[i], word) in emission:
            w_emission[i] = emission[(UNIVERSAL_TAGS[i], word)]
        else:
            w_emission[i] = np.log(epsilon)
    return w_emission

def viterbi_tagging(sentence, hmm_data):

    prior = hmm_data[0]
    transition = hmm_data[1]
    emission = hmm_data[2]

    N_words = len(sentence)

    trellis_val = np.zeros((N_words, N_tags)) - np.inf
    trellis_ind = np.zeros((N_words, N_tags), dtype=np.int32)

    trellis_val[0] = prior + lookup_emission(sentence[0], emission)

    for i in range(1, N_words):
        trellis_step = trellis_val[i-1][:, np.newaxis] + transition + lookup_emission(sentence[i], emission)
        trellis_val[i] = np.max(trellis_step, axis=0)
        trellis_ind[i] = np.argmax(trellis_step, axis=0)

    tags = [np.argmax(trellis_val[-1])]
    for i in range(N_words-1, 0, -1):
        tags.append(trellis_ind[i, tags[-1]])
    list.reverse(tags)
    
    return [UNIVERSAL_TAGS[tag_id] for tag_id in tags]

def tag_corpus(data, ind, hmm_data):
    
    m_ind = ind + [len(data)]
    tags = []
    
    for i in range(len(ind)):
        
        sentence = data[m_ind[i]:m_ind[i+1]]
        tags.extend(viterbi_tagging(sentence, hmm_data))
        
    return tags

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

    prior = compute_prior(pos_data, sent_inds)
    transition = compute_transition(pos_data, sent_inds)
    emission = compute_emission(pos_data, sent_inds)

    return prior, transition, emission
    

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.
    
    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    results = tag_corpus(pos_data, sent_inds, (prior, transition, emission))

    write_results(test_file_name+'.pred', results)

if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    #parameters = sys.argv
    #train_file_name = parameters[parameters.index("-d")+1]
    #test_file_name = parameters[parameters.index("-t")+1]
    train_file_name = "data/test-public-small"
    test_file_name = "data/test-public-small"

    # Start the training and tagging operation.
    tag (train_file_name, test_file_name)