# The tagger.py starter code for CSC384 A4.

import os
import sys

import numpy as np
from collections import Counter
from collections import defaultdict
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
    prior = np.zeros([N_tags])
    transition = np.zeros([N_tags, N_tags])
    emission = defaultdict(float)
    count_starting_tags = Counter()
    total_tags_ind = len(sent_inds)
    for i in sent_inds:
        start_word_tag = pos_data[i][1]
        count_starting_tags[start_word_tag] += 1
    for i in range(N_tags):
        tmp = (count_starting_tags[UNIVERSAL_TAGS[i]]) / total_tags_ind
        p = np.log(tmp) if tmp !=0 else float("-inf")
        prior[i] = p
    count_transition = Counter()
    count = 0
    while count < total_tags_ind:
        i = sent_inds[count]
        end = sent_inds[count+1] if count != total_tags_ind-1 else len(pos_data)
        while i < end-1:
            j = i + 1
            prev_tag, followed_tag = pos_data[i][1], pos_data[j][1]
            count_transition[prev_tag + '->' + followed_tag] += 1
            count_transition[prev_tag] += 1
            i += 1
        count += 1
    for i in range(N_tags):
        denominator = count_transition[UNIVERSAL_TAGS[i]]
        for j in range(N_tags):
            numerator = count_transition[UNIVERSAL_TAGS[i] + '->' + UNIVERSAL_TAGS[j]]
            transition[i][j] = np.log(numerator / denominator) if numerator !=0 else float("-inf")
    count_emission = Counter()
    count_tag = Counter()
    for i in range(len(pos_data)):
        word, tag = pos_data[i][0], pos_data[i][1]
        count_emission[(tag, word)] += 1
        count_tag[tag] += 1
    for key in count_emission:
        emission[key] = np.log(count_emission[key] / count_tag[key[0]])








    return prior, transition, emission
    

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')
    results = []
    min_emission = min(emission.values()) * 10
    for count in range(len(sent_inds)):
        start_index = sent_inds[count]
        end_index = sent_inds[count+1] if count != len(sent_inds)-1 else len(pos_data)
        prob_trellis = np.zeros([end_index-start_index, N_tags])
        for tag_i in range(N_tags):
            e_p = emission[(UNIVERSAL_TAGS[tag_i], pos_data[start_index].lower())]
            prob_trellis[0][tag_i] = prior[tag_i] * e_p * -1 if e_p != 0 else prior[tag_i] * min_emission * -1
        start_index += 1
        i = 1
        while start_index < end_index:
            for s in range(N_tags):
                word = pos_data[start_index].lower()
                e_p = emission[(UNIVERSAL_TAGS[s], word)]
                x = np.argmax(prob_trellis[i-1] * transition[:, s] * (e_p if e_p != 0 else min_emission))
                prob_trellis[i, s] = prob_trellis[i-1, x] * transition[x, s] * (e_p if e_p != 0 else min_emission)
            i += 1
            start_index += 1
        for i in range(prob_trellis.shape[0]):
            results.append(UNIVERSAL_TAGS[np.argmax(prob_trellis[i])])

    ####################
    # STUDENT CODE HERE
    ####################

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