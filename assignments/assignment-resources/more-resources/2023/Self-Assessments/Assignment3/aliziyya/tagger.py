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
    count = np.zeros(12)
    for n in sent_inds:
        starting = pos_data[n]
        count[UNIVERSAL_TAGS.index(starting[1])] += 1
    prior = (np.log(count/len(sent_inds)))

    ### Transition & Emission ###
    count_t = np.zeros((N_tags, N_tags))
    curr_ind = 0
    prev_pos = None
    count_e = {}
    for word, pos in pos_data:
        if curr_ind in sent_inds:       # first word of sentence
            # start of sentence
            prev_pos = pos
            curr_ind += 1
        else:                           
            # increment count_ti[prev_pos][curr_pos] 
            count_t[UNIVERSAL_TAGS.index(prev_pos)][UNIVERSAL_TAGS.index(pos)] += 1
            prev_pos = pos
            curr_ind += 1
        if count_e.get((pos, word)) == None:
            count_e[(pos, word)] = 1
        else:
            count_e[(pos, word)] += 1
    
    
    transition = count_t/count_t.sum(axis=1, keepdims=True)
    transition[transition == 0] = 1e-10
    transition = np.log(transition)
    total_pos = np.zeros(N_tags)
    for k, n in count_e.items():
        total_pos[UNIVERSAL_TAGS.index(k[0])] += n
    emission = {k:np.log(n/total_pos[UNIVERSAL_TAGS.index(k[0])]) for k, n in count_e.items()}
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
    final = []
    for i in range(len(sent_inds)):
        start = sent_inds[i]
        if i == (len(sent_inds)-1):
            end = len(pos_data)
        else:
            end = sent_inds[i+1]
       
        # Initialize trellises 
        prob_trellis = np.zeros((N_tags, end-start))
        path_trellis = []
        
        # Find the starting word designation
        for s in range(N_tags):
            if emission.get((UNIVERSAL_TAGS[s], pos_data[start])) != None:
                prob_trellis[s][0] = prior[s] * emission.get((UNIVERSAL_TAGS[s], pos_data[start]))
        
        # If starting word is not in prior array, choose most probable start        
        if (~prob_trellis[:,0].any(axis=0)).any():
            prob_trellis[:, 0] = 1e-10
            path_trellis.append(UNIVERSAL_TAGS[np.argmax(prior)])
        else: # If word DOES exist, want to choose the tag with the highest prob
            path_trellis.append(UNIVERSAL_TAGS[np.argmax(prob_trellis[:, 0])])
            
        # Find next word designation based on the assigned designation of previous and observed word    
        for o in range(start+1, end):
            for s in range(N_tags):
                if emission.get((UNIVERSAL_TAGS[s], pos_data[o])) != None:
                    calc = prob_trellis[:, o-start-1] * transition[s] * emission.get((UNIVERSAL_TAGS[s], pos_data[o]))
                    prob_trellis[s][o-start] = calc[np.argmax(calc)]
                    #path_trellis.append(UNIVERSAL_TAGS[s])
            # if word is not in trained emissions, choose most probable 
            if (~prob_trellis[:,o-start].any(axis=0)).any():
                for s in range(N_tags):
                    calc = prob_trellis[:, o-start-1] * transition[s] * np.log(1e-10)
                    prob_trellis[s][o-start] = calc[np.argmax(calc)]
                path_trellis.append(UNIVERSAL_TAGS[np.argmax(prob_trellis[:, o-start])])   
            else:
                path_trellis.append(UNIVERSAL_TAGS[np.argmax(prob_trellis[:, o-start])])
        final += path_trellis

    write_results(test_file_name+'.pred', final)

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

    