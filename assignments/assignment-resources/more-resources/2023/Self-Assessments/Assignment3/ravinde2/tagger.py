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

    prior = [0,0,0,0,0,0,0,0,0,0,0,0]
    
    transition = np.zeros((N_tags, N_tags))
    end_sentence_count = [0,0,0,0,0,0,0,0,0,0,0,0]
    
    for ind in sent_inds:
        priorfind(pos_data[ind], prior)
    ind_count = 1    
    for count in range(len(pos_data) - 1):
        if(count != sent_inds[ind_count] - 1):
            for tag in range(N_tags):
                if(UNIVERSAL_TAGS[tag] == pos_data[count][1]):
                    end_sentence_count[tag] += 1
            transitionfind(transition, pos_data[count + 1], pos_data[count])

        elif(ind_count < len(sent_inds) - 1 ):
            ind_count += 1

            

    emission = emissionfind(pos_data)


    for total in range(len(prior)):
        if(len(sent_inds) != 0 ):
            prior[total] = np.log(prior[total] /len(sent_inds))
        else:
            prior[total] = 0
    prior = np.round(prior, 8)
    print(end_sentence_count)
    for row in range(len(transition)):
        tag_total = end_sentence_count[row]
        if(tag_total != 0):
            transition[row] = np.log(np.divide(transition[row], [tag_total]))
        else:
            transition[row] = [0,0,0,0,0,0,0,0,0,0,0,0]
    
    return prior, transition, emission



    
def priorfind(word, prior):
    for i in range(len(UNIVERSAL_TAGS)):
        if(word[1] == UNIVERSAL_TAGS[i]):
            prior[i] += 1
            break




def emissionfind(pos_data):
    emission_prim = Counter(pos_data)
    emission_final = {}
    count_per_tag = {"VERB":0, "NOUN":0, "PRON":0, "ADJ":0, "ADV":0, "ADP":0, "CONJ":0, "DET":0,"NUM":0 ,"PRT":0, "X":0, ".":0}
    for key in emission_prim.keys():
        newkey = (key[1], key[0])
        emission_final[newkey] = emission_prim[key]
        for tag in UNIVERSAL_TAGS:
            if tag == key[1]:
                count_per_tag[tag] += emission_prim[key]
                break
            
    for key in emission_final.keys():
        emission_final[key] = np.log(emission_final[key]/count_per_tag[key[0]])

    return emission_final




def transitionfind(transition, word, prev_word):
    leave = False
    for tag_col in range(len(UNIVERSAL_TAGS)):
        for tag_row in range(len(UNIVERSAL_TAGS)):
            if(UNIVERSAL_TAGS[tag_row] == word[1] and UNIVERSAL_TAGS[tag_col] == prev_word[1]):
                transition[tag_col][tag_row] += 1
                leave = True
        if(leave):
            leave = False
            break




    
def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    

    write_results(test_file_name+'.pred', results)

if __name__ == '__main__':
    """
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d")+1]
    test_file_name = parameters[parameters.index("-t")+1]

    # Start the training and tagging operation.
    tag (train_file_name, test_file_name)
    """
    """
    prior = [0,0,0,0,0,0,0,0,0,0,0,0]
    priorfind(0,0,("The", "DET"), prior)
    print(prior)
    priorfind(1,0,("Fulton", "NOUN"), prior)
    print(prior)
    priorfind(25,25,("The", "DET"), prior)
    print(prior)
    """
    """
    print(emissionfind([("The", "DET"), ("Fulton", "NOUN"), ("County", "NOUN"),
                        ("The", "DET"), ("produced", "VERB")]))
    """
    """
    transition = np.zeros((N_tags, N_tags))
    transitionfind(transition, ("The", "DET"), ("Fulton", "NOUN"))
    transitionfind(transition, ("Fulton", "NOUN"), ("County", "NOUN"))
    print(transition)
    """
    train_HMM("data/train-public")
    """
    prior, transition, emission = train_HMM("test")
    print(transition)
    """
    
    
