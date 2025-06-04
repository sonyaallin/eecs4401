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

    # build HMM and train using forward algorithm

    prior = build_prior_table(pos_data, sent_inds)
    transition = build_trans_table(pos_data, sent_inds)
    emission = build_emis_table(pos_data)

    return prior, transition, emission


def build_prior_table(pos_data, sent_inds):

    sentence_starts = [pos_data[index][1] for index in sent_inds]
    num_sentences = len(sent_inds)

    tag_counts = Counter(sentence_starts)
    return np.log([tag_counts[tag]/num_sentences for tag in UNIVERSAL_TAGS])


def build_trans_table(pos_data, sent_inds):
    # joint(tag_j, tag_i) = count of tag_i followed by tag_j / count of tag_i - count of tag_i followed by '.'
    return np.array([list(np.log([P_cond(pos_data, sent_inds,  tag_j,tag_i) for tag_j in UNIVERSAL_TAGS])) for tag_i in UNIVERSAL_TAGS])


def build_emis_table(pos_data):
    # count number of references to each tag
    emis_dict = {}
    tags_count = Counter([pair[1] for pair in pos_data])

    # use dictionary to count tag, word references
    for i in range(len(pos_data)):
        word, tag = pos_data[i]
        if (tag, word) not in emis_dict:
            emis_dict[(tag, word)] = 1
        else:
            emis_dict[(tag, word)] += 1

    # emission[(tag,word)] = # of tag, word references / # of tag references
    for key in tags_count.keys():
        keys = [emis_key for emis_key in emis_dict.keys() if key == emis_key[0]]
        for new_key in keys:
            emis_dict[new_key] = np.log(emis_dict[new_key]/tags_count[key])

    return emis_dict


def P_cond(pos_data, sent_inds, A, B):
    count_BA = 0
    count_B = 0
    for i in range(len(pos_data)-1):
        word1, tag1 = pos_data[i]
        word2, tag2 = pos_data[i+1]
        if tag1 == B and tag2 == A and i+1 not in sent_inds:
            count_BA += 1
        if tag1 == B and i+1 not in sent_inds:
            count_B += 1

    return count_BA/count_B


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    # calculate tag probabilities for each sentence
    results = sentence_prob(pos_data, UNIVERSAL_TAGS, prior, transition, emission, sent_inds)

    print(results)
    write_results(test_file_name+'.pred', results)


def viterbi(O, S, Pi, A, B):
    # viterbi algorithm from lecture
    prob_trellis = np.zeros((len(S), len(O)))
    path_trellis = np.zeros((len(S), len(O))).tolist()
    for s in range(len(S)):
        if (UNIVERSAL_TAGS[s], O[0]) not in B:
            B[(UNIVERSAL_TAGS[s], O[0])] = 0.001
        prob_trellis[s, 0] = Pi[s]*B[(UNIVERSAL_TAGS[s], O[0])]
        path_trellis[s][0] = UNIVERSAL_TAGS[s]
    for o in range(1, len(O)):
        for s in range(len(S)):
            if (UNIVERSAL_TAGS[s], O[o]) not in B:
                B[(UNIVERSAL_TAGS[s], O[o])] = 0.001
            x = np.argmax(prob_trellis[:, o-1] * A[:, s] * B[UNIVERSAL_TAGS[s], O[o]])
            prob_trellis[s, o] = prob_trellis[x, o-1] * A[x, s] * B[UNIVERSAL_TAGS[s], O[o]]
            path_trellis[s][o] = UNIVERSAL_TAGS[s]
    return prob_trellis, path_trellis


def sentence_prob(O, S, Pi, A, B, sent_inds):
    results = []
    sent_inds += [len(O)]
    for i in range(len(sent_inds)-1):
        prob_trellis, path_trellis = viterbi(O[sent_inds[i]:sent_inds[i+1]], S, Pi, A, B)
        for j in range(len(prob_trellis[0])):
            x = np.argmax(prob_trellis[:, j])
            results.append(UNIVERSAL_TAGS[x])

    return results


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