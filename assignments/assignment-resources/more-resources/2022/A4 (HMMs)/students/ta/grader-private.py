import numpy as np
import signal
import time

from tagger import *
from collections import defaultdict

class TimeOutException(Exception):
    pass

def alarm_handler(signum, frame):
    raise TimeOutException()

def read_data_test(path):
    return open(path, 'r').read().split('\n')

def test_tagging(test_file):
	pred = np.asarray(read_data_test(test_file+'.pred'))
	soln = np.asarray(read_data_test(test_file+'.soln')[:-1])

	acc = np.sum(pred==soln) / len(soln)
	pct = min(acc, tagging_threshold) / tagging_threshold

	return pct

def almost_equal(a, b, diff=1e-4):
	if a == -np.inf:
		return b == -np.inf
	return np.abs(a-b) < diff

def array_almost_equal(a, b, diff=1e-4):
	if a.shape != b.shape:
		return False
	a_flat = a.flatten()
	b_flat = b.flatten()
	for i in range(a_flat.shape[0]):
		if not almost_equal(a_flat[i], b_flat[i]):
			return False
	return True

scheme = {
	'prior_a': 7,
	'prior_b': 7,
	'transition_a':7,
	'transition_b':7,
	'emission_a':7,
	'emission_b':7,
	'tagging_small':35,
	'tagging_large':23
}

tagging_threshold = 0.85

test_names = list(scheme.keys())

if __name__ == '__main__':

	#name = "student"
	name = sys.argv[1]
	fname = sys.argv[2]
	gname = name + "_results.txt"

	results = defaultdict(float)
	solutions = np.load('/Users/JaglalLab/Desktop/csc384-a3/ta/soln/soln-private-1.npz')
	signal.signal(signal.SIGALRM, alarm_handler)

	signal.alarm(60)
	try:
		prior, transition, emission = train_HMM('/Users/JaglalLab/Desktop/csc384-a3/ta/data/private/train-private-1')
	except TimeOutException as ex:
		g.write("TimeOutException when training: {}\n".format(ex))
	except Exception as e:
		g.write("Exception when training: {}\n".format(e))

	signal.alarm(60)
	try:
		prior_2, transition_2, emission_2 = train_HMM('/Users/JaglalLab/Desktop/csc384-a3/ta/data/private/train-private-1')
	except TimeOutException as ex:
		g.write("TimeOutException when training: {}\n".format(ex))
	except Exception as e:
		g.write("Exception when training: {}\n".format(e))

	# Prior Tests
	g = open(gname, "a")
	signal.alarm(60)
	try:
		assert(array_almost_equal(prior, solutions['prior']))
		results['prior_a'] = scheme['prior_a']
	except TimeOutException as ex:
		g.write("TimeOutException when testing prior: {}\n".format(ex))
	except Exception as e:
		g.write("Exception when testing prior: {}\n".format(e))

	signal.alarm(60)
	try:
		assert(almost_equal(np.sum(np.exp(prior_2)), 1))
		results['prior_b'] = scheme['prior_b']
	except TimeOutException as ex:
		g.write("TimeOutException when testing prior: {}\n".format(ex))
	except Exception as e:
		g.write("Exception when testing prior: {}\n".format(e))

	# Transition Tests
	signal.alarm(60)
	try:
		assert(array_almost_equal(transition, solutions['transition']))
		results['transition_a'] = scheme['transition_a']
	except TimeOutException as ex:
		g.write("TimeOutException when testing transition: {}\n".format(ex))
	except Exception as e:
		g.write("Exception when testing transition: {}\n".format(e))

	signal.alarm(60)
	try:
		assert(array_almost_equal(np.sum(np.exp(transition), axis=1), np.ones(N_tags)))
		results['transition_b'] = scheme['transition_b']
	except TimeOutException as ex:
		g.write("TimeOutException when testing transition: {}\n".format(ex))
	except Exception as e:
		g.write("Exception when testing transition: {}\n".format(e))

	# Emission Tests
	signal.alarm(60)
	try:
		assert(array_almost_equal(np.asarray([emission[(key[0], key[1])] for key in solutions['emission_key']]), solutions['emission_val']))
		results['emission_a'] = scheme['emission_a']
	except TimeOutException as ex:
		g.write("TimeOutException when testing emission: {}\n".format(ex))
	except Exception as e:
		g.write("Exception when testing emission: {}\n".format(e))

	signal.alarm(60)
	try:
		for tag in UNIVERSAL_TAGS:
			assert(almost_equal(np.sum(np.exp([emission_2[key] for key in emission_2 if key[0]==tag])), 1))
		results['emission_b'] = scheme['emission_b']
	except TimeOutException as ex:
		g.write("TimeOutException when testing emission: {}\n".format(ex))
	except Exception as e:
		g.write("Exception when testing emission: {}\n".format(e))

	# Tagging tests
	signal.alarm(60)
	# Small
	try:
		results['tagging_small'] = test_tagging('/Users/JaglalLab/Desktop/csc384-a3/ta/data/private/test-private-small-1') * scheme['tagging_small']
	except TimeOutException as ex:
		g.write("TimeOutException when tagging small corpus: {}\n".format(ex))
	except Exception as e:
		g.write("Exception when tagging small corpus: {}\n".format(e))

	signal.alarm(120)
	# Large
	try:
		results['tagging_large'] = test_tagging('/Users/JaglalLab/Desktop/csc384-a3/ta/data/private/test-private-large-1') * scheme['tagging_large']
	except TimeOutException as ex:
		g.write("TimeOutException when tagging large corpus: {}\n".format(ex))
	except Exception as e:
		g.write("Exception when tagging large corpus: {}\n".format(e))

	signal.alarm(0)
	res = ",".join([str(i) for i in scheme.values()])

	f = open(fname, "a")
	f.write("{}, {}\n".format(name, res))
	f.close()

	print("{},{}\n".format(name, res))

	#print(list(scheme.values()))
	#for t in test_names:
	#	print(t+": %.1f/%.1f" % (results[t], scheme[t]))
	#print("[Total]: %.1f/%.1f" % (np.sum([results[t] for t in test_names]), np.sum([scheme[t] for t in test_names])))

