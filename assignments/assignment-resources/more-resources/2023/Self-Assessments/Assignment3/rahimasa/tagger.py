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
    first_word_setenence = {}
    tags_to_words = {}
    prev_tag_to_tag = {}
    for tag in UNIVERSAL_TAGS:
        first_word_setenence[tag] = []
        tags_to_words[tag] = {}
        prev_tag_to_tag[tag] = {}
        for tag2 in UNIVERSAL_TAGS:
            tags_to_words[tag][tag2]=1e-5
            # prev_tag_to_tag[tag][tag2]=1e-5
    pos_data = read_data_train(train_file_name+'.txt')
    sent_inds = read_data_ind(train_file_name+'.ind')
    txt_index = 0
    ind_index = 0
    prev_tag = None
    num_of_first=0
    while txt_index< len(pos_data):
        word = pos_data[txt_index][0]
        tag = pos_data[txt_index][1]
        if txt_index == sent_inds[ind_index]:
            # print(word, tag)
            prev_tag= None
            num_of_first+=1
            first_word_setenence[tag].append(word)
            ind_index= min(len(sent_inds)-1, ind_index+1)
        if word in tags_to_words[tag]:
            tags_to_words[tag][word] += 1
        else:
            tags_to_words[tag][word] = 1
        if prev_tag is not None:
            if tag in prev_tag_to_tag[prev_tag]:
                prev_tag_to_tag[prev_tag][tag] += 1
            else:
                prev_tag_to_tag[prev_tag][tag] = 1
        prev_tag = tag
        txt_index+=1
    # print(pos_data)
    # print(sent_inds)
    # print(first_word_setenence)
    prior = np.array([0.0]*len(UNIVERSAL_TAGS))
    emission = {}
    for tag_i in range(len(UNIVERSAL_TAGS)):
        tag = UNIVERSAL_TAGS[tag_i]
        prior[tag_i] = np.log(len(first_word_setenence[tag])/num_of_first)
    transition= np.array([[0.0]*len(UNIVERSAL_TAGS)]* len(UNIVERSAL_TAGS))
    # print(transition)
    # print(prev_tag_to_tag.keys())
    for i in range(len(UNIVERSAL_TAGS)):
        # print(prev_tag_to_tag[UNIVERSAL_TAGS[i]])
        # print(sum(prev_tag_to_tag[UNIVERSAL_TAGS[i]].values()))
        for j in range(len(UNIVERSAL_TAGS)):
            if UNIVERSAL_TAGS[j] not in prev_tag_to_tag[UNIVERSAL_TAGS[i]]:
                transition[i][j]=np.log(0)
            else:
                transition[i][j] = np.log(prev_tag_to_tag[UNIVERSAL_TAGS[i]][UNIVERSAL_TAGS[j]]/sum(prev_tag_to_tag[UNIVERSAL_TAGS[i]].values()))
    for tag_i in range(len(UNIVERSAL_TAGS)):
        tag = UNIVERSAL_TAGS[tag_i]
        words_with_tag = sum(tags_to_words[tag].values())
        for word, occurences in tags_to_words[tag].items():
            emission[(tag, word)] = np.log(occurences/words_with_tag)
        
    # print(sum(prior))
    ####################
    # STUDENT CODE HERE
    ####################
    
    return prior, transition, emission
    
def viterbi(pos_data, start, end, prior, transition, emission):
    # print(start,end)
    trellis = np.array(len(UNIVERSAL_TAGS)*[[0]*(end-start+1)])
    paths =  np.array(len(UNIVERSAL_TAGS)*[[0]*(end-start+1)])
    # print("new", pos_data[start])
    for tag in range(len(UNIVERSAL_TAGS)):
        if ((UNIVERSAL_TAGS[tag], pos_data[start])) in emission:
            trellis[tag][0]= prior[tag]+ emission[(UNIVERSAL_TAGS[tag], pos_data[start])]
        else:
            trellis[tag][0]= prior[tag]+ np.log(1e-5)
        # paths[tag][0]=[UNIVERSAL_TAGS[tag]]
        # print(trellis[tag][0], UNIVERSAL_TAGS[tag])
    # i= start+1
    # while i<=end:
    #     for tag_i in range(len(UNIVERSAL_TAGS)):
    #         tag= UNIVERSAL_TAGS[tag_i]
    #         emission_val= np.log(1e-5)
    #         if (tag, pos_data[i]) in emission: 
    #             emission_val= emission[(tag, pos_data[i])]
                
    #         l = [(trellis[x][i-1]+transition[x][tag_i]+ emission_val,x) for x in range(len(UNIVERSAL_TAGS))]
    #         x= max(l, key=lambda t: t[0])[1]
    #         # print(x, l)
    #         # print(emission[(tag, pos_data[i])])
    #         # print(trellis[x][i-1])
    #         # print(transition[x][tag_i])
    #         trellis[tag_i][i-start]= trellis[x][i-1]+transition[x][tag_i]+ emission_val
    #         paths[tag_i][i-start]= x
    #     i+=1
    i= 1
    while start+i <=end:
        for tag_i in range(len(UNIVERSAL_TAGS)):
            tag = UNIVERSAL_TAGS[tag_i]
            emission_val = np.log(1e-5)
            if (tag, pos_data[i+start]) in emission:
                emission_val = emission[(tag, pos_data[i+start])]
            l = [(trellis[x][i-1]+transition[x][tag_i]+ emission_val,x) for x in range(len(UNIVERSAL_TAGS))]
            x = max(l, key=lambda t: t[0])[1]
            trellis[tag_i][i] = trellis[x][i-1]+transition[x][tag_i]+ emission_val
            paths[tag_i][i]= x
        i+=1
    result=[]
    l = [(trellis[k][end-start], k) for k in range(len(UNIVERSAL_TAGS))]
    k = max(l, key= lambda t: t[0])[1]
    for j in range(end-start, -1, -1):
        result= [UNIVERSAL_TAGS[k]]+ result
        k= paths[k][j]
    # print("HII",result)
    return result
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
    # print(pos_data)
    results=[]
    for i in range(len(sent_inds)-1):
        start = sent_inds[i]
        end= sent_inds[i+1]-1
        results= results+ viterbi(pos_data, start, end, prior, transition, emission)
    results+= viterbi(pos_data, sent_inds[-1], len(pos_data)-1, prior, transition, emission)
    # print(results)
    # print(pos_data)
    # print(sent_inds)
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