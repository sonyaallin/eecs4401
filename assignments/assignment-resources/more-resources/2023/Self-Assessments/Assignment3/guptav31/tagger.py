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
    ### Prior ###
    pos_counts = np.zeros(12)
    for n in sent_inds:
        #start = pos_data[n]
        pos_counts[UNIVERSAL_TAGS.index(pos_data[n][1])] += 1
    prior = (np.log(pos_counts/len(sent_inds)))

    ### Transition & Emission ###
    trans_counts = np.zeros((N_tags, N_tags))
    curr = 0
    prev_pos = None
    emiss_counts = {}
    for word, pos in pos_data:
        #Two cases, either the current word is the first word, and has no transitions,
        #or the current word had a word before it, so there is a transition
        #For emissions, the observed outcome is the word, and the probality is P(word|tag),
        #or the probability of the word given the tag
        
        if curr in sent_inds:       # first word of sentence
            # start of sentence, no transition, so don't update trans_counts
            prev_pos = pos
            curr += 1
            if emiss_counts.get((pos, word)) != None: 
                emiss_counts[(pos, word)] += 1
            else:
                emiss_counts[(pos, word)] = 1
        else:                           
            trans_counts[UNIVERSAL_TAGS.index(prev_pos)][UNIVERSAL_TAGS.index(pos)] += 1    #There was a previous word, update trans_counts 
            prev_pos = pos
            curr += 1
            if emiss_counts.get((pos, word)) != None:
                emiss_counts[(pos, word)] += 1
            else:
                emiss_counts[(pos, word)] = 1
        
    
    total_trans_counts = trans_counts.sum(axis=1, keepdims=True)
    transition = trans_counts/total_trans_counts
    transition[transition == 0] = 1e-20
    transition = np.log(transition)
    
    total_pos = np.zeros(N_tags)
    for k, n in emiss_counts.items():
        total_pos[UNIVERSAL_TAGS.index(k[0])] += n
    
    emission = {}
    for k, n in emiss_counts.items():
        emission[k] = np.log(n/total_pos[UNIVERSAL_TAGS.index(k[0])])

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
    results = []
    for i in range(len(sent_inds)):
        first = sent_inds[i]
        if i == (len(sent_inds)-1):
            last = len(pos_data)
        else:
            last = sent_inds[i+1]
       
        #Two trellises needed, one to hold the max probability of the path leading to a state, one to hold the path itself
        prob_trellis = np.zeros((N_tags, last-first))
        path_trellis = []
        
        #If the starting word is in the emissions, get the probability of the word given each pos, multiply with the probabilty of that pos being the starting word
        #store product in prob_trellis
        #If the starting word is not in the emissions, i.e. it wasn't previously encountered in training, assign just the prior probability, since there is no further information
        for s in range(N_tags):
            emission_prob = emission.get((UNIVERSAL_TAGS[s], pos_data[first]))
            if emission_prob != None:
                prob_trellis[s][0] = emission_prob * prior[s] 
            else:
                prob_trellis[s][0] = prior[s] 
        
        #Tag with highest probability should be appended to path_trellis
        path_trellis.append(UNIVERSAL_TAGS[np.argmax(prob_trellis[:, 0])])
            
        #Find the optimal tag for the rest of the words 
        #Multiply the transition probability of going from a previous pos to the pos, s
        #with each value in the prob_trellis for the previous word
        #If the word was in training data, multiply in the emission probability
        #If it was not, multiply by the log of a small default value 
        for o in range(first+1, last):
            for s in range(N_tags):
                emission_prob = emission.get((UNIVERSAL_TAGS[s], pos_data[o])) 
                if emission_prob != None:
                    all_probs = prob_trellis[:, o-first-1] * transition[s] * emission.get((UNIVERSAL_TAGS[s], pos_data[o]))
                    prob_trellis[s][o-first] = np.amax(all_probs)
                else:
                    all_probs = prob_trellis[:, o-first-1] * transition[s] * np.log(1e-20)
                    prob_trellis[s][o-first] = np.amax(all_probs)
            #update path trellis
            path_trellis.append(UNIVERSAL_TAGS[np.argmax(prob_trellis[:, o-first])])
                    
        results += path_trellis

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
