import math
import random
from typing import List
import time


#####
# DEFINITION TODO
# candidate: 
# guess:
# result:
#####


def is_candidate(candidate: List[int], guess: List[int], result: List[int]):
    """
    Given a cantidate answer and the guess we are testing,
    Check if the mask provided is identical to the result
    """
    unmatched_letters = guess[:]

    for i in range(6):
        letter = guess[i]
        if letter == candidate[i]:
            if result[i] != 3:
                return False
            unmatched_letters.remove(letter)
        elif letter in candidate:
            if result[i] != 2:
                return False
            unmatched_letters.remove(letter)
        else:
            if result[i] != 1:
                return False

    return True


def encode(word: str) -> List[int]:
    """
    encode a word to a list of integer with the index of the letter
    65 = 'A'
    """
    return [ord(c) - 65 for c in word]

def decode(seq: List[int]) -> str:
    """
    decode a list of int to a word
    """
    return "".join([chr(x + 65) for x in seq])


def filter_choices(seq: List[List[int]], guess: List[int], result: List[int]):
    """
    filter the list to keep only valid words
    """
    return [x for x in seq if is_candidate(x, guess, result)]


def pick_best_choice(seq: List[List[int]]) -> List[int]:
    """
    Get the next value to guess
    """
    if len(seq) < 250:
        return make_guess(seq)
    else:
        return best_opener(seq)



def get_mask(candidate: List[int], guess: List[int]) -> List[int]:
    """
    Get the result for a candidate word and a made guess
    This function is too slow for now
    """
    letter_states = [1, 1, 1, 1, 1, 1]

    unmatched_letters = guess[:]

    for i in range(6):
        if guess[i] == candidate[i]:
            letter_states[i] = 3
            unmatched_letters.remove(guess[i])
        elif guess[i] in candidate:
            letter_states[i] = 2
            unmatched_letters.remove(guess[i])

    return letter_states

def e(c, t):
    """
    Compute the entropy given a count and a total
    """
    p = c / t
    return -p * math.log2(p)

def make_guess(words: List[List[int]]):
    """
    For each word, compute the mask for every other words
    This result is then used to compute the entropy of the word
    and then the best guess
    """
    max_entropy = -1
    best_guess = [0, 0, 0, 0, 0, 0]

    n = 12500 // len(words)
    k = min(n, len(words))
    # k = len(words)
    for guess in words:
        bins = {}
        s = random.sample(words, k=k)
        for candidate in s:
            mask = get_mask(candidate, guess)
            m_str = "".join(map(str, mask))
            bins[m_str] = bins.get(m_str, 0) + 1

        new_entropy = sum(e(i, k) for i in bins.values())
        if new_entropy > max_entropy:
            max_entropy = new_entropy
            best_guess = guess

    return best_guess



def best_opener(words: List[List[int]]) -> List[int]:
    """
    For each position of letter, compute the distribution of letter
    Then compute the entropy for every words being the entropy per letter
    Used in the first turn to reduce as much as possible the options
    """
    c = [[0 for _ in range(26)] for i in range(6)]

    total = len(words)
    for guess in words:
        for i, letter in enumerate(guess):
            c[i][letter] += 1

    max_entropy = -1
    best_guess = [0, 0, 0, 0, 0, 0]
    for guess in words:
        entropy = 0.0
        for i, letter in enumerate(guess):
            entropy += e(c[i][letter], total)
    
        if entropy > max_entropy:
            max_entropy = entropy
            best_guess = guess
    
    return best_guess


def load_words():
    with open("wordlist.txt", "r") as f:
        words = f.read().splitlines()
    return words

def load_testcases():
    with open("test_cases.txt", "r") as f:
        words = f.read().splitlines()
    return words


def main(words: List[str], answer: str):

    words_encoded = [encode(word) for word in words]
    answer_encoded = encode(answer)

    # print("\nWords remaining:", len(words_encoded), file=sys.stderr)

    guess = None
    for i in range(10):
        if guess is not None:
            states = get_mask(answer_encoded, guess)

        if guess is not None:
            words_encoded = filter_choices(words_encoded, guess, states) 
            # print("Words remaining:", len(words_encoded), file=sys.stderr)

        guess = pick_best_choice(words_encoded)

        # print(decode(guess), answer)
        if decode(guess) == answer:
            return i+1
    return 10


if __name__ == "__main__":
    import cProfile

    random.seed(21)
    words = load_words()
    # answers = load_testcases()
    answers = random.sample(words, 150)

    start = time.time()
    with cProfile.Profile() as pr:
        total_turns = 0
        for answer in answers:
            total_turns += main(words, answer)
        pr.dump_stats("profile.txt")
    stop = time.time()
    print("\n\nTotal Score:", total_turns)
    print("Time taken:", stop - start)
