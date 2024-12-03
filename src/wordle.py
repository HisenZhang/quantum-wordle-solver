import random

class Wordle:
    def __init__(self, dictionary_path):
        self.word_list = self._load_dictionary(dictionary_path)
        self.target_word = None
        self.guesses = []
        self.attempts = 0

    def _load_dictionary(self, path):
        with open(path, 'r') as f:
            return {word.strip().lower() for word in f if len(word.strip()) == 5}

    def start_game(self):
        self.target_word = random.choice(list(self.word_list))
        self.guesses = []
        self.attempts = 0
        return {'attempts': self.attempts}

    def make_guess(self, guess):
        guess = guess.lower()
        if guess not in self.word_list:
            return {'error': 'Word not in dictionary', 'attempts': self.attempts}
            
        self.attempts += 1
        result = self._evaluate_guess(guess)
        self.guesses.append({'word': guess, 'result': result})
        
        return {
            'result': result,
            'attempts': self.attempts
        }

    def _evaluate_guess(self, guess):
        result = []
        target = list(self.target_word)
        
        for i, letter in enumerate(guess):
            if letter == target[i]:
                result.append('correct')
                target[i] = None
            else:
                result.append(None)
        
        for i, letter in enumerate(guess):
            if result[i] is None:
                if letter in target:
                    result[i] = 'present'
                    target[target.index(letter)] = None
                else:
                    result[i] = 'absent'
        
        return result

    def get_game_state(self):
        return {
            'attempts': self.attempts,
            'guesses': self.guesses
        }