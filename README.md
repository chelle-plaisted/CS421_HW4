# CS421_HW4
HOMEWORK 4: GENETIC ALGORITHM

The plan:

Design notes: may want separate objects for Gene, Population..., or just represent with data structures

-Gene: a representation of the layout of the game
	-required layout components: Anthill location, tunnel location, grass location, enemy food location (probably in terms of distance from drop off sources)
	-strategy: group together components that in connection with one another form a strategy so they don't get separated accross generations.
		-This may involve adding extra components (???)
			- Don't want something that can't be crossed/mutated, easily
		-Grass should be grouped.

-Data representation:
	- Gene: an array, length X
	- Fitness: an array, length Y (number of games won out of 10 games by corresponding gene from population)
		- may need to have structure to map index to score if we use sorting at all for the parent-pairing.
	- Current population: list of gene arrays, length 10
	- index: int, gene to be evalutated
	- gamesPlayed: int, # of games played by currently evaluated gene, default: 0
	- Notes:
		start with small population size: 10 --> 100+
	
-To determine the best layout:

1. initializePop(): Initialize the population of genes with random values and reset the fitness list to default values
	-randomization of genes, ensure validity: 
		-Anthill, tunnel, grass can only go in valid, un-used locations on AI/current player's side of the board
		-enemy food can only go in unused, valid squares on their side of the board.
	-default fitness score: 0

2. generateChildren(parent1, parent2): take 2 parents and generate 2 children with chance of mutation
	- determine a random (?) crossover point within the length of the parents.
	- Use python slicing to generate child1 and child2. [Note: do NOT use for-loop]
	- Add children to some data structure for the next generation (?). (Note: I don't think we can overwrite the current population)
	- n% chance of mutation as follows:
		- Any of the layout components can be mutated to a new, STILL VALID location

3. makeNextGen(): Make the next generation of children by selecting the most fit parents.
	- Note: parents can be selected more than once (or else you can't maintain a population of the same  size and still weed out old parents)
	- technique: weighted randomization
		- via https://en.wikipedia.org/wiki/Selection_(genetic_algorithm):
			- normalize fitness function values: divide each by the sum of all
			- sort by fitness function values (descending)
			- accumulated fitness value: my fitness + sum of all fitnesses before me
				-CHECK: last fitness accumulated should be = 1.
			- generate random number, R< b/w 0 and 1
			- select the last individual whose accumulated normalized value is greater than or equal to R.
		- if ^ is too computationally demanding: use stochastic acceptance (aka fitness proportionate selection/roulette-wheel selection)
			- variants: stochastic universal sampling, tournament selection (best of random subset), truncation selection (take best proportion of population, i.. 1/3, 1/2)
			- only look at those with fitness > xx
			- retain a few of the best individuals in the population. 

4. getPlacement(): Use the current to-be-evaluated gene (stored in index) to determine the game placement.

5. registerWin(): Do the following.
	- Update the fitness score of current gene.
		- See index for gene.
		- +1 for win.
		- -1 for loss.
		- penalty/bonus for number of turns (?)
			- note: turns, not moves
	- Are we done evaluating this gene?
		- i.e. you want to play Z games per gene.
		- increment gamesPlayed
	- Advance to the next gene: increment index pointer, set gamesPlayed = 0
		- If all genes have been evaluated (index = genes.length):
			- for evidence file: asciiPrintState() the state and the score of the highest fitness gene
			- call makeNextGen()
			- set index = 0

Evidence file/Process: 

1. use the asciiPrintState in register win to record the best performing gene of each generation >> evidence file
2. Run a tournament (at least 20 generations):
	-# games = population size * # games per gene * # generations

See assignment sheet for turn in instructions
