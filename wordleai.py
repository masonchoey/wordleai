from graphics import *
import tkinter as tk
import random
import math
import csv
########### get to the icloud:######################
#cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/wordleai/
####################################################
#BASELINE AVERAGE: 4.2

########### ALL TOGGLABLE VARIABLES: ##################
#developer window:
dev_window = False
#developer window width
dev_window_width = 600
#yellow weight
yellow_weight = 1
green_importance = 1.55
#green weight
green_weight = yellow_weight * green_importance
#width of the screen
screen_width = 500
#height of the screen
screen_height = 800
#toggle the animations:
toggle_animation = True
#delay before starting the next game(seconds)
delay = 10
######################################################

#whether or not the window is running
running = True
#create the window
if dev_window:
	win = GraphWin("Wordle", screen_width+dev_window_width, screen_height)
else:
	win = GraphWin("Wordle", screen_width, screen_height)
#variables
#list of all the guessable words(12973)
list_of_words = []
#list of remaining words
list_of_possible_words = []
#all solutions (2315):
solutions_list = []
#temporary removal list
removal_list = []
#size of the boxes
box_size = 62
#space between the boxes
margin = 10
#grid's top left point
grid_x = (screen_width - (box_size * 5) - (margin * 4))/2
grid_y = 240
#generate actual 5x6 grid for each guess
text_grid = []
#grid to update the screen
rect_grid = []
#number of times the user has already guessed words
num_guesses = 0
#list of number of guesses
dict_of_num_guesses = {}
#maximum number of guesses
max_guesses = 7
#total guesses
total_guesses = 0
#number of rounds
num_rounds = 0
#most number of guesses
most_guesses = 0
#least number of guesses
least_guesses = max_guesses
#count of how many times it doesn't guess a word from the solutions
non_solution_count = 0
#current computer guess
guess = ""
#user guess
user_guess = ""
#user input
user_input = ""
#guess override is from the four greens scenario
guess_override = ""
#temp list to record the keystrokes
temp_list = []
#user's streak:
streak = 0
#has the user guessed it yet?
guessed = False
#is the game over?
game_over = False
#first game to see if the setup function should be called when the start game button is pressed
first_game = True
#actual word:
wordle = ""
#list of all the wordle letters
wordle_letters = []
#best streak (fetch from a csv file)
best = open("best.txt", "r")
best.seek(0)
best_streak = best.read()
best.close()
#dictionary of average guesses:
dict_average_guesses = {}
#remaining words:
amount_of_remaining_words = []
#index
index = 0

#################### FUNCTIONS #####################################

#function to redraw the text
def draw_text(text, size, fill, style, redraw, font):
	if redraw == True:
		text.undraw()
	text.setSize(size)
	if fill != "none":
		text.setFill(fill)
	if style != "none":
		text.setStyle(style)
	if font != "none":
		text.setFace(font)
	text.draw(win)

#toggle the command to check for the keyboard
game_running = False
def startgame():
	global first_game
	global game_running
	if game_running == False:
		game_running = True
		# if first_game == False:
		# 	setup()
		# else:
		# 	first_game = False

#returns all words with the letter in that position
def get_words(all_possible_words, letter, position):
	return_list = []
	for word in all_possible_words:
		if word[position-1] == letter:
			return_list.append(word)
	return return_list

def score_word(all_possible_words, guess_word, green_weight, yellow_weight):
	guess_word_score = 0
	for word in all_possible_words:
		#same approach with num appearances but this time to check for doubles in the scoring
		num_appearances = {}
		for i in range(len(word)):
			if word[i] in num_appearances:
				num_appearances[word[i]] += 1
			else:
				num_appearances[word[i]] = 1
		# green box
		for i in range(len(word)):
			if word[i] == guess_word[i]:
				guess_word_score += green_weight
				num_appearances[word[i]] -= 1
				# print("green: " + word[i])
		# yellow box
		for i in range(len(guess_word)):
			if word[i] in guess_word and num_appearances[word[i]] > 0:
				guess_word_score += yellow_weight
				num_appearances[word[i]] -= 1
				# print("yellow: " + word[i])
			#check if guessing yellow in the same place as previously
	return guess_word_score

def check_for_four_greens(list_of_possible_words):
	#base_word is arbitrarily picked
	base_word = list_of_possible_words[0]
	#loop through the possible words
	for i in range(len(list_of_possible_words)):
		#score is used to see if it shares four words with the starting word
		score = 0
		#loop through the word
		for j in range(len(list_of_possible_words[i])):
			if list_of_possible_words[i][j] == base_word[j]:
				score += 1
		if score < 4:
			return False
	return True

def four_green_letters(list_of_possible_words, list_of_words):
	index = 0
	possible_letters_dict = {}
	#first identify where the different letter is:
	for i in range(len(list_of_possible_words[0])):
		if list_of_possible_words[0][i] != list_of_possible_words[1][i]:
			index = i	
	#then compile a list of all the possible letters
	for word in list_of_possible_words:
		possible_letters_dict[word[index]] = 1
		#check the thing for duplicate letters
		for j in range(len(word)):
			if word[j] == word[index] and j != index:
				possible_letters_dict[word[index]] += 1
	#then score all the 12000 words based on how helpful they are in this scenario:
	score_dict = {}
	for word in list_of_words:
		#reset the scores everytime a new word is checked:
		for possible_word in list_of_possible_words:
			possible_letters_dict[possible_word[index]] = 1
			#check the thing for duplicate letters
			for j in range(len(possible_word)):
				if possible_word[j] == possible_word[index] and j != index:
					possible_letters_dict[possible_word[index]] += 1
		score_dict[word] = 0
		#loops through the word
		for letter in word:
			if letter in possible_letters_dict:
				if possible_letters_dict[letter] >= 1:
					if possible_letters_dict[letter] == 1:
						score_dict[word] += 1
					possible_letters_dict[letter] -= 1
	# print(sorted(score_dict.items(), key=lambda x: x[1], reverse=True))
	return(max(score_dict, key=score_dict.get))

#################### SETUP #########################################
#this is for creating another game again
def setup():
	global wordle
	global wordle_letters
	global best_streak
	global index

	list_of_words.clear()
	list_of_possible_words.clear()
	#open the file
	all_solutions = open("all_solutions.txt", "r")
	for word in all_solutions:
		solutions_list.append(word)
	all_solutions.close()

	all_guesses = open("all_guessable_words.txt", "r")
	for word in all_guesses:
		list_of_words.append(word.strip("\n"))
		list_of_possible_words.append(word.strip("\n"))
	all_guesses.close()

	#actual word selected (generate a new word when the game is restarted):
	# wordle = solutions_list[random.randint(0,len(solutions_list)-1)]
	wordle = solutions_list[index]
	wordle = wordle[0:5] #cut off the extra dumbass space
	# wordle = "tight" #tight, rater, hatch
	#list of letters in the word:
	wordle_letters = []
	for i in range(len(wordle)):
		wordle_letters.append(wordle[i])

	#old stuff list is to prevent flashing on the screen
	old_stuff = []
	for item in win.items[:]:
		old_stuff.append(item)
	#set the background color
	win.setBackground("#1F1F1F")
	#put the start buttons
	start_button = tk.Button(win,text="Start Game",bg="#3389FF",command=startgame())
	# start_button.place(x=screen_width/2 - 50,y=700,width=100,height=30)

	#generate the grids
	text_grid.clear()
	rect_grid.clear()
	for row in range(max_guesses):
		text_grid.append([])
		rect_grid.append([])
		for column in range(5):
			text_grid[row].append(" ")
	#make them appear on the window
	for row in range(max_guesses):
		for column in range(5):
			#position the rectangles correctly then draw them to the window
			rect = Rectangle(Point(grid_x + box_size * column + margin * (column-1), grid_y + box_size * row + margin * (row-1)),Point(grid_x + box_size * (column+1) + margin * (column-1), grid_y + box_size * (row+1) + margin * (row-1)))
			rect_color = "#3a3a3c" #gray
			rect.setFill(rect_color)
			rect_text = Text(Point(grid_x + box_size * column + margin * (column-1) + box_size/2, grid_y + box_size * row + margin * (row-1) + box_size/2), text_grid[row][column])
			if toggle_animation == True:
				rect.draw(win)
				draw_text(rect_text, 18, "white", "bold", False, "none")
			rect_grid[row].append([rect,rect_text,rect_color])

		#generate the WORDLE AI title
		title = Text(Point(screen_width/2, 100), "WORDLE AI")
		title.setFill("white")
		title.setSize(36)
		title.setFace("courier")

		#generate the streak text
		streak_text = Text(Point(120, 180), "Streak: " + str(streak))
		streak_text.setFill("white")
		streak_text.setSize(18)
		streak_text.setFace("courier")

		#generate the best streak text
		best_streak_text = Text(Point(screen_width-150, 180), "Best Streak: " + str(best_streak))
		best_streak_text.setFill("white")
		best_streak_text.setSize(18)
		best_streak_text.setFace("courier")

		if dev_window:
			draw_text(Text(Point(screen_width + dev_window_width/2,180), "All remaining words:"), 26, "white", "none", False,"courier")

		if toggle_animation == True:
			title.draw(win)
			streak_text.draw(win)
			best_streak_text.draw(win)

	for item in win.items[:]:
		if item in old_stuff:
			item.undraw()
	# print(wordle_letters) #print the wordle letters here
	old_stuff.clear()

#call it once to create the game
setup()

# # score of each word
# sorted_list_of_words = {}
# for word in list_of_words:
# 	sorted_list_of_words[word] = math.floor(score_word(list_of_words, word, green_weight, yellow_weight))
# 	print(word)
# print(sorted(sorted_list_of_words.items(), key=lambda x: x[1], reverse=True))

# # write the new values onto it
# words_with_values = open("words_with_values_freq.csv", "w")
# for item in sorted_list_of_words:
# 	words_with_values.write(item + "," + str(sorted_list_of_words[item]) + ",")
# words_with_values.close()

# #add stuff to the dictionary
# for word in list_of_words:
# 	wordle_scores[word] = 0
count = 0
# index = 0
# remove_list = []
# #Prune the words:
# good_words = []
# for word in list_of_words:
# 	good_words.append(word)
# 	for i in range(len(word)):
# 		if word[i] == "b" or word[i] == "d" or word[i] == "f" or word[i] == "g" or word[i] == "h" or word[i] == "j" or word[i] == "k" or word[i] == "m" or word[i] == "p" or word[i] == "q" or word[i] == "v" or word[i] == "w" or word[i] == "x" or word[i] == "y" or word[i] == "z":
# 			print(word)
# 			remove_list.append(word)

# for word in remove_list:
# 	good_words.remove(good_words)

# print(good_words)
#################### RUNNING #######################################

start_time = time.time()
while running == True:
	if game_running == True:
		#DECISION MAKING: DECIDE WHICH WORDS TO USE(for now guess the word with the highest score)
		#This is from the four greens stuff
		#check for the guess override
		# print(len(list_of_possible_words), check_for_four_greens(list_of_possible_words),num_guesses)
		if len(list_of_possible_words) > 2 and check_for_four_greens(list_of_possible_words):
			guess_override = four_green_letters(list_of_possible_words,list_of_words)
		if guess_override == "":
			if num_guesses >= 1:
				#find the best scoring word now with the remaining list of possible words
				values_dict = {}
				for word in list_of_possible_words:
					values_dict[word] = score_word(list_of_possible_words, word, green_weight, yellow_weight)
			else:
				# get the existing dictionary
				words_with_values = open("words_with_values_freq.csv", "r")
				values_list = words_with_values.read().split(",")
				values_dict = {}
				words_with_values.close()
				#convert the csv from a list into a dictionary
				i = 0
				while i < len(values_list)-1:
					values_dict[values_list[i]] = values_list[i+1]
					i += 2
			best_score = 0
			for word in list_of_possible_words:
				if int(values_dict[word]) > best_score:
					best_score = int(values_dict[word])
					best_key = word
			guess = best_key
			# if num_guesses == 0:
				# guess = "arose"
		else:
			guess = guess_override
			guess_override = ""
		################# END OF DECISION MAKING ##################

		for i in range(len(guess)):
			#this should update the text_grid at an appropriate value
			text_grid[num_guesses][i] = guess[i].capitalize()
			#update the rect_grid
			rect_grid[num_guesses][i][1] = Text(rect_grid[num_guesses][i][0].getCenter(), text_grid[num_guesses][i])
			if toggle_animation == True:
				#redraw it to the grid
				draw_text(rect_grid[num_guesses][i][1], 18, "white", "bold", True, "none")

		guess = guess.lower()
		if guess in list_of_words:
			#solve the issue of two letters in the same word:
			#this dictionary keeps track of how many different times each letter is in the wordle
			num_appearances = {}
			for i in range(len(wordle)):
				if wordle[i] in num_appearances:
					num_appearances[wordle[i]] += 1
				elif wordle[i] in wordle_letters:
					num_appearances[wordle[i]] = 1

			#this dictionary keeps track of how many times each letter is in the GUESS
			guess_num_appearances = {}
			guess_letters = []
			for i in range(len(guess)):
				guess_letters.append(guess[i])
			for i in range(len(guess)):
				if guess[i] in guess_num_appearances:
					guess_num_appearances[guess[i]] += 1
				elif guess[i] in guess_letters:
					guess_num_appearances[guess[i]] = 1

			#check for green boxes
			for i in range(len(guess)):
				if guess[i] == wordle_letters[i]:
					if num_appearances[guess[i]] > 0:

						#reduce the remaining times it appears in the letter:
						num_appearances[guess[i]] -= 1
						#update the rect grid:
						rect_grid[num_guesses][i][2] = "#538d4e" #green

						#update the possible words
						for word in list_of_possible_words:
							if word[i] != guess[i]:
								removal_list.append(word)

						#dont remove the original word
						if guess in removal_list:
							removal_list.remove(guess)

						#remove them all at the end
						for word in removal_list:
							list_of_possible_words.remove(word)
						removal_list.clear()

						if toggle_animation == True:
							#redraw the rectangle
							rect_grid[num_guesses][i][0].setFill(rect_grid[num_guesses][i][2])
							rect_grid[num_guesses][i][0].undraw()
							rect_grid[num_guesses][i][0].draw(win)
							#redraw the text on top of the rectangle
							rect_grid[num_guesses][i][1].undraw()
							draw_text(rect_grid[num_guesses][i][1], 18, "white", "bold", True,"none")

			#check for yellow boxes(prioritize the green boxes first with this method)
			for i in range(len(guess)):
				if guess[i] in wordle_letters:
					if num_appearances[guess[i]] > 0 and rect_grid[num_guesses][i][2] != "#538d4e":
						#reduce the remaining times it appears in the letter:
						num_appearances[guess[i]] -= 1
						#update the rect grid:
						rect_grid[num_guesses][i][2] = "#b59f3b" #yellow

						#update the possible words
						for word in list_of_possible_words:
							word_dict = {}
							for j in range(len(word)):
								if word[j] not in word_dict:
									word_dict[word[j]] = 1
								elif word[j] in word_dict:
									word_dict[word[j]] += 1
							if guess[i] not in word_dict:
								removal_list.append(word)
							elif word[i] == guess[i]:
								removal_list.append(word)

						#dont remove the original word
						if guess in removal_list:
							removal_list.remove(guess)

						#remove them all at the end
						for word in removal_list:
							list_of_possible_words.remove(word)
						removal_list.clear()
						
						if toggle_animation == True:
							#redraw the rectangle
							rect_grid[num_guesses][i][0].setFill(rect_grid[num_guesses][i][2])
							rect_grid[num_guesses][i][0].undraw()
							rect_grid[num_guesses][i][0].draw(win)
							#redraw the text on top of the rectangle
							rect_grid[num_guesses][i][1].undraw()
							draw_text(rect_grid[num_guesses][i][1], 18, "white", "bold", True,"none")

			#this dictionary keeps track of how many different times each letter is in the wordle
			num_appearances = {}
			for i in range(len(wordle)):
				if wordle[i] in num_appearances:
					num_appearances[wordle[i]] += 1
				elif wordle[i] in wordle_letters:
					num_appearances[wordle[i]] = 1

			#now do gray boxees to update the guesses left
			for i in range(len(guess)):
				if guess[i] not in wordle_letters:
					#update the possible words
					for word in list_of_possible_words:
						word_dict = {}
						for j in range(len(word)):
							if word[j] not in word_dict:
								word_dict[word[j]] = 1
							elif word[j] in word_dict:
								word_dict[word[j]] += 1
						#if the guess[i] that isnt in the wordle letters but is in the word_dict, then pop it
						if guess[i] in word_dict and guess != word:
							removal_list.append(word)

				elif guess[i] in wordle_letters:
					if guess_num_appearances[guess[i]] > num_appearances[guess[i]]:
						#update the possible words
						#first creat a num appearances dictionary for each word
						for word in list_of_possible_words:
							word_dict = {}
							for j in range(len(word)):
								if word[j] not in word_dict:
									word_dict[word[j]] = 1
								elif word[j] in word_dict:
									word_dict[word[j]] += 1
							#then see if it has the same or more amount of that letter (ie swiss)
							if word_dict[guess[i]] >= guess_num_appearances[guess[i]]:
								removal_list.append(word)

				#dont remove the original word
				if guess in removal_list:
					removal_list.remove(guess)

				#remove them all at the end
				for word in removal_list:
					list_of_possible_words.remove(word)
				removal_list.clear() 

			#check if the user guessed the word
			if guess == wordle:
				guessed = True
				game_over = True

			#increase the number of guesses and remove the guess from the list of possible words
			if guess in list_of_possible_words:
				list_of_possible_words.remove(guess)

			if game_over == False:
				amount_of_remaining_words.append(len(list_of_possible_words))
			else:
				amount_of_remaining_words.append("✔")
			#generate the text of remaining word on the right side
			if toggle_animation == True:
				draw_text(Text(Point(450,230+box_size/2 + (num_guesses*(box_size+margin))),amount_of_remaining_words[len(amount_of_remaining_words)-1]), 15, "white", "bold", False, "courier")
				if dev_window and game_over == False:
					draw_list = []
					if len(list_of_possible_words) > 10:
						if len(list_of_possible_words) >= 20:
							draw_list = list_of_possible_words[:20]
							draw_list.append("...")
							#split it into 2 lines
							draw_text(Text(Point(screen_width + dev_window_width/2,230+box_size/4 + (num_guesses*(box_size+margin))),draw_list[:10]), 15, "white","none", False, "courier")
							draw_text(Text(Point(screen_width + dev_window_width/2,230+3*box_size/4 + (num_guesses*(box_size+margin))),draw_list[10:21]), 15, "white","none", False, "courier")
						else:
							draw_list = list_of_possible_words
							#split it into 2 lines
							draw_text(Text(Point(screen_width + dev_window_width/2,230+box_size/4 + (num_guesses*(box_size+margin))),draw_list[:10]), 15, "white","none", False, "courier")
							draw_text(Text(Point(screen_width + dev_window_width/2,230+3*box_size/4 + (num_guesses*(box_size+margin))),draw_list[10:]), 15, "white","none", False, "courier")
					else:
						#keep it as one
						draw_list = list_of_possible_words
						draw_text(Text(Point(screen_width + dev_window_width/2,230+box_size/2 + (num_guesses*(box_size+margin))),draw_list[:10]), 15, "white","none", False, "courier")

			num_guesses += 1
		if num_guesses == max_guesses:
			game_over = True


		################## GAME OVER #####################
		if game_over == True:
			end_time = time.time()
			print(end_time - start_time)
			start_time = time.time()
			count += 1
			if count == 2314:
				count = 0
				dict_of_num_guesses.clear()
				dict_average_guesses[green_importance] = total_guesses/num_rounds
				green_importance += 0.05
				#green weight
				green_weight = yellow_weight * green_importance
				print(green_weight, yellow_weight, dict_average_guesses)
				num_rounds = 0
				total_guesses = 0


			if num_guesses in dict_of_num_guesses:
				dict_of_num_guesses[num_guesses] += 1
			else:
				dict_of_num_guesses[num_guesses] = 1
			if guessed == True:
				if toggle_animation == True:
					#draw the winning text
					winning_text = Text(Point(screen_width/2, 750), "Congrats! You guessed the word!")
				#update the streak:
				streak += 1
			elif guessed == False:
				if toggle_animation == True:
					#draw the losing
					winning_text = Text(Point(screen_width/2, 750), "You lost. The word was " + wordle)
				#update the streak:
				streak = 0
			if toggle_animation == True:
				#draw it to the window
				winning_text.setFill("white")
				winning_text.setSize(18)
				winning_text.setFace("courier")
				winning_text.draw(win)
			#see if the streak is better than the best
			if streak > int(best_streak):
				best_streak = streak
				best = open("best.txt", "w+")
				best.write(str(best_streak))
				best.close()

			#recalculate the averages:
			if num_guesses < least_guesses:
				least_guesses = num_guesses
			if num_guesses > most_guesses:
				most_guesses = num_guesses
			num_rounds += 1
			total_guesses += num_guesses
			print("\nWord: " + wordle + ", Guesses: " + str(num_guesses) + " ")
			print("Average number of guesses: " + str(total_guesses/num_rounds))
			printList = []
			for key in sorted(dict_of_num_guesses):
				printList.append((key, dict_of_num_guesses[key]))
			print("Frequency of each number of guesses: " + str(printList))
			print("Minimum: " + str(least_guesses))
			print("Maximum: " + str(most_guesses))
			print("Rounds played: " + str(num_rounds))

			#restart the game:
			game_over = False
			game_running = False
			guessed = False
			num_guesses = 0
			index += 1
			amount_of_remaining_words.clear()
			time.sleep(delay)
			setup()

		# #get the existing dictionary
		# words_with_values = open("words_with_values_freq.csv", "r")
		# values_list = words_with_values.read().split(",")
		# values_dict = {}
		# words_with_values.close()
		# words_with_values = open("words_with_values_freq.csv", "w")
		# #write the new values onto it
		# i = 0
		# while i < len(values_list)-1:
		# 	values_dict[values_list[i]] = values_list[i+1]
		# 	i += 2
		# values_dict[guess] = score_word(list_of_words,guess)
		# for item in values_dict:
		# 	words_with_values.write(item + "," + str(values_dict[item]) + ",")
		# words_with_values.close()


#################### TESTING SHIT ##################################

#test for probability of different words containing a yellow box:
# word_is = 0
# word_not = 0
# for i in range(1000):
# 	word_not += 1
# 	wordle = list_of_words[random.randint(0,len(list_of_words)-1)]
# 	for j in range(len(wordle)):
# 		if wordle[j] == "x" or wordle[j] == "y" or wordle[j] == "l":
# 			word_is += 1
# 			word_not -= 1
# 			break

# # test the frequency of all the letters
# letter_dict = {}
# for word in list_of_words:
# 	for i in range(len(word)):
# 		if word[i] not in letter_dict:
# 			letter_dict[word[i]] = 1
# 		else:
# 			letter_dict[word[i]] += 1
# print(letter_dict)
# #download to a csv file:
# letter_appearance = open("letter_appearance.txt", "w+")
# for letter in letter_dict:
# 	letter_appearance.write(letter + "," + str(letter_dict[letter]) + "\n")
# letter_appearance.close()

# #test of unique words with each letter
# letter_dict_2 = {}
# for word in list_of_words:
# 	set1 = set()
# 	for i in range(len(word)):
# 		set1.add(word[i])
# 	for set_item in (set1):
# 		if set_item not in letter_dict_2:
# 			letter_dict_2[set_item] = 1
# 		elif set_item in letter_dict_2:
# 			letter_dict_2[set_item] += 1
# print(letter_dict_2)
# #download to a csv file:
# unique_words_per_letter = open("unique_words_per_letter.txt", "w+")
# for letter in letter_dict_2:
# 	unique_words_per_letter.write(letter + "," + str(letter_dict_2[letter]) + "\n")
# unique_words_per_letter.close()

# #see how many times each letter appears in each position
# letter_dict_3 = {}
# for word in list_of_words:
# 	for i in range(len(word)):
# 		if word[i] + str(i+1) not in letter_dict_3:
# 			letter_dict_3[word[i] + str(i+1)] = 1
# 		else:
# 			letter_dict_3[word[i] + str(i+1)] += 1

# #download to a csv file:
# letter_per_position = open("letter_per_position.txt", "w+")
# for letter in letter_dict_3:
# 	letter_per_position.write(letter + "," + str(letter_dict_3[letter]) + "\n")
# letter_per_position.close()

# print("Number of times each letter appears in all 5 letter words: ")
# print(sorted(letter_dict.items(), key=lambda x: x[1], reverse=True))
# print("Number of unique words with each letter: ")
# print(sorted(letter_dict_2.items(), key=lambda x: x[1], reverse=True))
# print("Number of times each letter appears in each position: ")
# print(sorted(letter_dict_3.items(), key=lambda x: x[1], reverse=True))


