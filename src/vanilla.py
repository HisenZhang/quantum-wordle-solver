class VanillaWordleSolver:
    def __init__(self, word_list):
        self.possible_words = set(word_list)
        self.feedback_history = []
        
        
    def update_possibilities(self, guess, feedback):
        pass
        
    def get_next_guess(self):
        guess = self.possible_words.pop()
        return guess
        

# from wordle import Wordle    
    
# game = Wordle('../unique_words.txt')
# solver = VanillaWordleSolver(game.word_list)
# game.start_game()

# while True:
#     guess = solver.get_next_guess()
#     result = game.make_guess(guess)
#     if all(x == 'correct' for x in result['result']):
#         break
    
# print(game.get_game_state())