# The tagger.py starter code for CSC384 A4.

import os
import sys

import numpy as np
from collections import Counter

ZERO = np.log(1e-5)
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

def get_prior(pos_data, sent_inds):
    """
    Return the initial probalities of each POS in a table of size N_tags
    - Each entry corresponds to the prior log probability of seeing the i'th tag in UNIVERSAL_TAGS at the beginning of a sequence
    - i.e. prior[i] = log P(tag_i)
    """
    # extract POS at sent indices (starting tokens of each sequence)
    data = np.array(pos_data)
    start_tokens = data[sent_inds]
    start_tokens = start_tokens[:, 1] # only need POS
    N = len(start_tokens)
    
    # count # occurences of each tag, build distribution
    prior = np.array([len(start_tokens[start_tokens==tag_i]) for tag_i in UNIVERSAL_TAGS])

    # convert frequency list into log probabilties (Note: x/N == log(x)-log(N))
    prior = np.log(prior) - np.log(N)

    return prior

def get_sentences(pos_data, sent_inds):
    """
    Return array of sequences (i.e. split by sentence)
    - if sent_inds is not empty, assume first index is 0 (i.e. can't start middle of sequence)
    - if sent_inds is empty, entire training example is one sequence 
    """
    if not sent_inds:
        return [pos_data] # only one sentence, can't skip first idx
    sentences = np.split(pos_data, sent_inds[1:], axis=0) # skip index 0
    return sentences

def get_transitions(sentences):
    """
    Return the transition probabilities from each POS at state=i to each POS at state=j, where i<j (j=i+1)
    - The (i,j)'th entry stores the log probablity of seeing the j'th tag given it is a transition coming from the i'th tag in UNIVERSAL_TAGS
    - i.e. transition[i, j] = log P(tag_j|tag_i)
    """
    # frequency matrix for tag_i x tag_j
    transition = np.zeros(N_tags*N_tags).reshape([N_tags, N_tags])

    # count frequency of each type of transition
    for sent in sentences:
        tag_i = sent[0][1] # previous pos
        for token, tag_j in sent[1:]:
            idx_i = UNIVERSAL_TAGS.index(tag_i)
            idx_j = UNIVERSAL_TAGS.index(tag_j)
            transition[idx_i, idx_j]+=1
            tag_i=tag_j # shift current -> previous tag

    # get frequency of tag i
    row_N = transition.sum(axis=1) # get row-wise sum

    # convert frequency matrix into log probabilties (Note: x/N == log(x)-log(N))
    # ignore warning of divide by zero encountered in log
    transition = np.log(transition) - np.log(np.vstack(row_N))
    return transition


def get_emissions(pos_data):
    """
    Return dictionary with {key:value} = {(TAG, WORD): log probability of observing WORD given a TAG}
    - Each key in the dictionary refers to a (TAG, WORD) pair
    - The TAG must be an element of UNIVERSAL_TAGS, however the WORD can be anything that appears in the training data
    - The value corresponding to the (TAG, WORD) key pair is the log probability of observing WORD given a TAG
    - i.e. emission[(tag, word)] = log P(word|tag)
    - If a particular (TAG, WORD) pair has never appeared in the training data, then the key (TAG, WORD) should not exist.
    """
    # get distribution of (word, tag) tuples (i.e. split by unique rows)
    pos, pos_count = np.unique(pos_data, axis=0, return_counts=True)

    # get distribution of tags
    tags, tag_count = np.unique(np.array(pos_data)[:,1], return_counts=True)
    tag_dict = {tags[i]:tag_count[i] for i in range(N_tags)}

    # count fequency of each word i, then get ratio of word i to number of words with same tag 
    emission = { (pos[i, 1], pos[i, 0]):np.log(pos_count[i])-np.log(tag_dict[pos[i, 1]]) for i in range(len(pos))}
    return emission

def predict_sentence(prior, transition, emission, sentence):
    """
    Return list of predicted tags
    - prior: list of size N_tags, contains prob. distribution for start of sequence (i.e. prior[i] = log P(tag_i)  )
    - transition: N_tags*N_tags, contains prob. distribution for state X_t -> X_t+1 transitions for all tag combinations (i.e. transition[i, j] = log P(tag_j|tag_i)  )
    - emission: dictionary (i.e. emission[(tag, word)] = log P(word|tag)  )
    - sentence: list of (WORD, TAG)
    """
    res = []

    # get initial emission probailities for all tags (i.e. first word could be multiple tags => set prob., or NONE => set all other to ZERO )
    emission_0 = np.array(N_tags*[ZERO])
    tags_0 = [(UNIVERSAL_TAGS.index(t), (t,w)) for (t,w) in emission.keys() if w==sentence[0]]

    # set relevant initial emission probabilities
    for idx, key in tags_0:
        emission_0[idx] = emission[tuple(key)]
    
    # set probabilities, initialize paths for X_1
    prob_trellis = np.full((N_tags, len(sentence)), -np.inf)
    prob_trellis[:, 0] = (prior + emission_0)

    path_trellis = [[[t]] for t in UNIVERSAL_TAGS]

    # determine trellis values for X_2 -> X_n
    for i in range(1, len(sentence)):
        # get emissions for each tag (set to ZERO if word not found in emission)
        emission_i = list(map((lambda x : ZERO if (UNIVERSAL_TAGS[x], sentence[i]) not in emission else emission[(UNIVERSAL_TAGS[x], sentence[i])]), np.arange(N_tags)))
        for tag_j in range(N_tags):
            # select the path (i.e previous tag) to this node with most `promise'
            # for all prior tags x, find the best x that maximizes: P(E_i | X_i) * P(X_i | X_i-1) * F(X_i)
            x = np.argmax(np.exp(emission_i[tag_j] + transition[:, tag_j] + prob_trellis[:, i-1]))
            new_path = path_trellis[x][i-1] + [UNIVERSAL_TAGS[tag_j]]

            # build on the path of x for tag_j's path, add prediction to path trellis
            prob_trellis[tag_j, i] = emission_i[tag_j] + transition[x, tag_j] + prob_trellis[x, i-1]
            path_trellis[tag_j].append(new_path)

    # choose path with maximum probability at last state
    path = np.argmax(np.exp(prob_trellis[:, -1]))
    return path_trellis[path][-1]

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

    # get initial probabilities P(A_1)
    prior = get_prior(pos_data, sent_inds)
    
    # get transition probabilities P(A_t+1 | A_t)
    sentences = get_sentences(pos_data, sent_inds) # split into sentences
    transition = get_transitions(sentences)

    # get emission probabilities P(E_t | A_t)
    emission = get_emissions(pos_data)

    return prior, transition, emission
    

def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """
    prior, transition, emission = train_HMM(train_file_name)
    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    sentences = get_sentences(pos_data, sent_inds)
    results=[]
    for sent in sentences:
        results += predict_sentence(prior, transition, emission, sent)

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
    tag(train_file_name, test_file_name)