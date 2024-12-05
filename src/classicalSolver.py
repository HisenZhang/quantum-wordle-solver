class VanillaWordleSolver:
    def __init__(self, word_list, **kwargs):
        self.possible_words = set(word_list)
        self.feedback_history = []
        
        
    def update_possibilities(self, guess, feedback):
        pass
        
    def get_next_guess(self):
        guess = self.possible_words.pop()
        return guess
        

class PruninghWordleSolver:
    def __init__(self, word_list, **kwargs):
        self.possible_words = set(word_list)
        self.feedback_history = []
        
    def update_possibilities(self, guess, feedback):
        new_possibilities = set()
        for word in self.possible_words:
            if self._matches_feedback(word, guess, feedback):
                new_possibilities.add(word)
        self.possible_words = new_possibilities
        self.feedback_history.append((guess, feedback))
        
    def get_next_guess(self):
        return next(iter(self.possible_words))
        
    def _matches_feedback(self, candidate, guess, feedback):
        for i, (letter, result) in enumerate(zip(guess, feedback)):
            if result == 'correct' and candidate[i] != letter:
                return False
            elif result == 'absent' and letter in candidate:
                return False
            elif result == 'present' and (letter not in candidate or candidate[i] == letter):
                return False
        return True
    
class FrequencyWordleSolver:
    def __init__(self, word_list, **kwargs):
        self.possible_words = set(word_list)
        self.feedback_history = []
        # Calculate letter frequencies once at initialization
        self.frequencies = self._calculate_initial_frequencies(word_list)
        
    def _calculate_initial_frequencies(self, word_list):
        frequencies = {}
        total_words = len(word_list)
        
        # Count letter occurrences
        for word in word_list:
            for letter in word:
                frequencies[letter] = frequencies.get(letter, 0) + 1
                
        # Convert to frequencies
        for letter in frequencies:
            frequencies[letter] /= total_words
            
        return frequencies
        
    def update_possibilities(self, guess, feedback):
        new_possibilities = set()
        for word in self.possible_words:
            if self._matches_feedback(word, guess, feedback):
                new_possibilities.add(word)
        self.possible_words = new_possibilities
        self.feedback_history.append((guess, feedback))
        
    def get_next_guess(self):
        # Score each word based on initial frequencies
        best_score = float('-inf')
        best_word = None
        
        for word in self.possible_words:
            # Score based on unique letters using pre-calculated frequencies
            score = sum(self.frequencies[letter] for letter in set(word))
            
            if score > best_score:
                best_score = score
                best_word = word
                
        return best_word if best_word else next(iter(self.possible_words))
        
    def _matches_feedback(self, candidate, guess, feedback):
        for i, (letter, result) in enumerate(zip(guess, feedback)):
            if result == 'correct' and candidate[i] != letter:
                return False
            elif result == 'absent' and letter in candidate:
                return False
            elif result == 'present' and (letter not in candidate or candidate[i] == letter):
                return False
        return True

# from wordle import Wordle    
    
# game = Wordle('../unique_words.txt')
# solver = LinearSearchWordleSolver(game.word_list)
# game.start_game()

# while True:
#     guess = solver.get_next_guess()
#     result = game.make_guess(guess)
#     if all(x == 'correct' for x in result['result']):
#         break
#     solver.update_possibilities(guess, result['result'])
    
# print(game.get_game_state())