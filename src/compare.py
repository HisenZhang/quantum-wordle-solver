import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np


from wordle import Wordle
from linearSearch import LinearSearchWordleSolver, FrequencyWordleSolver
from vanilla import VanillaWordleSolver

def compare_solvers(n_games=500):
    results = defaultdict(list)
    solvers = {
        # 'Vanilla': VanillaWordleSolver,
        'Feedback': LinearSearchWordleSolver,
        'Frequency': FrequencyWordleSolver
    }
    
    for solver_name, solver_class in solvers.items():
        for _ in range(n_games):
            game = Wordle('../unique_words.txt')
            solver = solver_class(game.word_list)
            game.start_game()
            
            # Track remaining possibilities for this game
            game_burndown = [len(solver.possible_words)]
            
            while True:
                guess = solver.get_next_guess()
                result = game.make_guess(guess)
                if all(x == 'correct' for x in result['result']):
                    break
                solver.update_possibilities(guess, result['result'])
                game_burndown.append(len(solver.possible_words))
            
            results[solver_name].append(game_burndown)

    plot_burndown(results)
    return results

def plot_burndown(results):
    plt.figure(figsize=(10, 6))
    
    colors = {'Vanilla': 'blue', 'Feedback': 'orange','Frequency':'green'}
    
    for solver_name, burndowns in results.items():
        # Plot individual traces with high transparency
        for trace in burndowns:
            plt.plot(trace, alpha=10/len(burndowns), color=colors[solver_name], linewidth=1)
            
        max_len = max(len(b) for b in burndowns)
        padded = [b + [1]*(max_len - len(b)) for b in burndowns]
        means = np.mean(padded, axis=0)
        plt.plot(means, 
                label=solver_name,
                color=colors[solver_name], 
                linestyle='-.',
                linewidth=3, 
                alpha=.5)
    
    plt.xlim(0,10)
    plt.yscale('log')
    
    plt.xlabel('Guess Number')
    plt.ylabel('Remaining Possibilities')
    plt.title('Wordle Solver Burndown Comparison')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.savefig("../result/figures/compare.png")
    plt.savefig("../result/figures/compare.pdf")
    plt.show()
    
results = compare_solvers()