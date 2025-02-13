from graphics import *
import tkinter as tk, random, math
from pynput import keyboard
########### get to the icloud:######################
#cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/
####################################################
#width of the screen
screen_width = 500
#height of the screen
screen_height = 800
#whether or not the window is running
running = True
#create the window
win = GraphWin("Wordle", screen_width, screen_height)
#variables
#list of all the words
list_of_words = []
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
#current user guess
user_guess = ""
#user input
user_input = ""
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
#gets rid of all letters in a list except for the 5 letter ones:
# list1 = []
# with open('words_alpha.txt') as f:
#     for line in f:
#         if len(line.rstrip('\n')) == 5:
#    	        list1.append(line.rstrip('\n'))
# words_alpha1 = open('words_alpha.txt', 'w+')
# for word in list1:
#     words_alpha1.write(word + "\n")
# words_alpha1.close()

words_alpha = open("words_alpha.txt", "r")
for word in words_alpha:
	list_of_words.append(word.strip("\n"))
words_alpha.close()

#################### FUNCTIONS #####################################

#function to redraw the text
def draw_text(text, size, fill, style, redraw):
	if redraw == True:
		text.undraw()
	text.setSize(size)
	if fill != "none":
		text.setFill(fill)
	if style != "none":
		text.setStyle(style)
	text.draw(win)

#toggle the command to check for the keyboard
keyboard_running = False
def startgame():
	global first_game
	global keyboard_running
	if keyboard_running == False:
		keyboard_running = True
		if first_game == False:
			setup()
		else:
			first_game = False

#returns all words with the letter in that position
def get_words(all_possible_words, letter, position):
	return_list = []
	for word in all_possible_words:
		if word[position-1] == letter:
			return_list.append(word)
	return return_list

def score_word(all_possible_words, guess_word):
	guess_word_score = 0
	for word in all_possible_words:
		#same approach with num appearances but this time to check for doubles in the scoring
		num_appearances = {}
		for i in range(len(guess_word)):
			if guess_word[i] in num_appearances:
				num_appearances[guess_word[i]] += 1
			else:
				num_appearances[guess_word[i]] = 1
		for i in range(len(word)):
			if word[i] == guess_word[i]:
				guess_word_score += 3
				num_appearances[word[i]] -= 1
		for i in range(len(guess_word)):
			if word[i] in guess_word and num_appearances[word[i]] > 0:
				guess_word_score += 2
				num_appearances[word[i]] -= 1
	return guess_word_score

#################### TESTING SHIT ##################################

#test for probability of different words containing a yellow box:
# fuzzy_is = 0
# fuzzy_not = 0
# for i in range(100000):
# 	fuzzy_not += 1
# 	wordle = list_of_words[random.randint(0,len(list_of_words)-1)]
# 	for j in range(len(wordle)):
# 		if wordle[j] == "f" or wordle[j] == "u" or wordle[j] == "z" or wordle[j] == "y":
# 			fuzzy_is += 1
# 			fuzzy_not -= 1
# 			break

#test the frequency of all the letters
# letter_dict = {}
# for word in list_of_words:
# 	for i in range(len(word)):
# 		if word[i] not in letter_dict:
# 			letter_dict[word[i]] = 1
# 		else:
# 			letter_dict[word[i]] += 1
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

# # score of each word
# sorted_list_of_words = {}
# for word in list_of_words:
# 	sorted_list_of_words[word] = score_word(list_of_words, word)
# 	print(word)
# print(sorted(sorted_list_of_words.items(), key=lambda x: x[1], reverse=True))

# print("Number of times each letter appears in all 5 letter words: ")
# print(sorted(letter_dict.items(), key=lambda x: x[1], reverse=True))
# print("Number of unique words with each letter: ")
# print(sorted(letter_dict_2.items(), key=lambda x: x[1], reverse=True))
# print("Number of times each letter appears in each position: ")
# print(sorted(letter_dict_3.items(), key=lambda x: x[1], reverse=True))


#################### SETUP #########################################
#this is for creating another game again
def setup():
	global wordle
	global wordle_letters
	global best_streak
	#set the background color
	win.setBackground("#1F1F1F")

	#old stuff list is to prevent flashing on the screen
	old_stuff = []
	for item in win.items[:]:
		old_stuff.append(item)
	#put the start buttons
	start_button = tk.Button(win,text="Start Game",bg="#3389FF",command=startgame)
	start_button.place(x=screen_width/2 - 50,y=700,width=100,height=30)

	#generate the grids
	text_grid.clear()
	rect_grid.clear()
	for row in range(6):
		text_grid.append([])
		rect_grid.append([])
		for column in range(5):
			text_grid[row].append(" ")

	#make them appear on the window
	for row in range(6):
		for column in range(5):
			#position the rectangles correctly then draw them to the window
			rect = Rectangle(Point(grid_x + box_size * column + margin * (column-1), grid_y + box_size * row + margin * (row-1)),Point(grid_x + box_size * (column+1) + margin * (column-1), grid_y + box_size * (row+1) + margin * (row-1)))
			rect_color = "#3a3a3c" #gray
			rect.setFill(rect_color)
			rect.draw(win)
			rect_text = Text(Point(grid_x + box_size * column + margin * (column-1) + box_size/2, grid_y + box_size * row + margin * (row-1) + box_size/2), text_grid[row][column])
			draw_text(rect_text, 18, "white", "bold", False)
			rect_grid[row].append([rect,rect_text,rect_color])

	#generate the WORDLE AI title
	title = Text(Point(screen_width/2, 100), "WORDLE AI")
	title.setFill("white")
	title.setSize(36)
	title.setFace("courier")
	title.draw(win)

	#generate the streak text
	streak_text = Text(Point(120, 180), "Streak: " + str(streak))
	streak_text.setFill("white")
	streak_text.setSize(18)
	streak_text.setFace("courier")
	streak_text.draw(win)

	#generate the best streak text
	best_streak_text = Text(Point(screen_width-150, 180), "Best Streak: " + str(best_streak))
	best_streak_text.setFill("white")
	best_streak_text.setSize(18)
	best_streak_text.setFace("courier")
	best_streak_text.draw(win)


	#actual word selected (generate a new word when the game is restarted):
	wordle = list_of_words[random.randint(0,len(list_of_words)-1)]
	#list of letters in the word:
	wordle_letters = []
	for i in range(len(wordle)):
		wordle_letters.append(wordle[i])
	for item in win.items[:]:
		if item in old_stuff:
			item.undraw()
	print(wordle_letters) #print the wordle letters here
	old_stuff.clear()

#call it once to create the game
setup()
#################### RUNNING #######################################

def on_press(key):
    try:
        k = key.char
    except:
        k = key.name
    temp_list.append(k)
    return False

while running == True:
	if keyboard_running == True:
		with keyboard.Listener(on_press=on_press,) as listener:
				listener.join()
		user_input = temp_list[0]
		temp_list = []
		#if the user inputted a backspace, then delete the previous guess
		if user_input == "backspace":
			user_guess = user_guess[0:-1]
			#remove the text from the screen
			rect_grid[num_guesses][len(user_guess)][1].undraw()
		if len(user_input) == 1 and len(user_guess) < 5:
			user_guess += user_input.capitalize()
			#this should update the text_grid at an appropriate value
			text_grid[num_guesses][len(user_guess)-1] = user_input.capitalize()
			#update the rect_grid
			rect_grid[num_guesses][len(user_guess)-1][1] = Text(rect_grid[num_guesses][len(user_guess)-1][0].getCenter(), text_grid[num_guesses][len(user_guess)-1])
			#redraw it to the grid
			draw_text(rect_grid[num_guesses][len(user_guess)-1][1], 18, "white", "bold", True)
		if user_input == "enter" and len(user_guess) == 5:
			user_guess = user_guess.lower()
			if user_guess in list_of_words:
				#solve the issue of two letters in the same word:
				#this dictionary keeps track of how many different times each letter is in the wordle
				num_appearances = {}
				for i in range(len(wordle)):
					if wordle[i] in num_appearances:
						num_appearances[wordle[i]] += 1
					elif wordle[i] in wordle_letters:
						num_appearances[wordle[i]] = 1
				#check for green boxes
				for i in range(len(user_guess)):
					if user_guess[i] == wordle_letters[i]:
						if num_appearances[user_guess[i]] > 0:
							#reduce the remaining times it appears in the letter:
							num_appearances[user_guess[i]] -= 1
							#update the rect grid:
							rect_grid[num_guesses][i][2] = "#538d4e" #green
							#redraw the rectangle
							rect_grid[num_guesses][i][0].setFill(rect_grid[num_guesses][i][2])
							rect_grid[num_guesses][i][0].undraw()
							rect_grid[num_guesses][i][0].draw(win)
							#redraw the text on top of the rectangle
							rect_grid[num_guesses][i][1].undraw()
							draw_text(rect_grid[num_guesses][i][1], 18, "white", "bold", True)
				#check for yellow boxes(prioritize the green boxes first with this method)
				for i in range(len(user_guess)):
					if user_guess[i] in wordle_letters:
						if num_appearances[user_guess[i]] > 0 and rect_grid[num_guesses][i][2] != "#538d4e":
							#reduce the remaining times it appears in the letter:
							num_appearances[user_guess[i]] -= 1
							#update the rect grid:
							rect_grid[num_guesses][i][2] = "#b59f3b" #green
							#redraw the rectangle
							rect_grid[num_guesses][i][0].setFill(rect_grid[num_guesses][i][2])
							rect_grid[num_guesses][i][0].undraw()
							rect_grid[num_guesses][i][0].draw(win)
							#redraw the text on top of the rectangle
							rect_grid[num_guesses][i][1].undraw()
							draw_text(rect_grid[num_guesses][i][1], 18, "white", "bold", True)
				#check if the user guessed the word
				if user_guess == wordle:
					guessed = True
					game_over = True
				#increase the number of guesses and reset the user guess
				user_guess = ""
				num_guesses += 1
			else:
				for i in range(len(user_guess)):
					#flash all the squares red
					#update the rect grid:
					rect_grid[num_guesses][i][2] = "#a33e3e" #red
					#redraw the rectangle
					rect_grid[num_guesses][i][0].setFill(rect_grid[num_guesses][i][2])
					rect_grid[num_guesses][i][0].undraw()
					rect_grid[num_guesses][i][0].draw(win)
					draw_text(rect_grid[num_guesses][i][1], 18, "white", "bold", True)
				time.sleep(0.35)
				for i in range(len(user_guess)):
					#flash all the squares red
					#update the rect grid:
					rect_grid[num_guesses][i][2] = "#3a3a3c" #gray
					#redraw the rectangle
					rect_grid[num_guesses][i][0].setFill(rect_grid[num_guesses][i][2])
					rect_grid[num_guesses][i][0].undraw()
					rect_grid[num_guesses][i][0].draw(win)
					draw_text(rect_grid[num_guesses][i][1], 18, "white", "bold", True)
		if num_guesses == 6 and guessed == False:
			game_over = True
		if game_over == True:
			if guessed == True:
				#draw the winning text
				winning_text = Text(Point(screen_width/2, 750), "Congrats! You guessed the word!")
				#update the streak:
				streak += 1
			elif guessed == False:
				#draw the losing
				winning_text = Text(Point(screen_width/2, 750), "You lost. The word was " + wordle)
				#update the streak:
				streak = 0
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
			#restart the game:
			game_over = False
			keyboard_running = False
			num_guesses = 0
	if keyboard_running == False:
		win.update_idletasks()
		win.update()
