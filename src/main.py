from wordle import Wordle

game = Wordle()
game.start_game()
result = game.make_guess('crane')
print(result)
state = game.get_game_state()
print(state)