words_with_values = open("all_guessable_words.txt", "r")
values_list = words_with_values.read().split("\n")
values_dict = {}
words_with_values.close()
print(values_list)
#convert the csv from a list into a dictionary
i = 0
while i < len(values_list)-1:
	values_dict[values_list[i]] = values_list[i+1]
	i += 2


for word in values_list:
	list1 = []
	for i in range(len(word)):
		list1.append(word[i])
	if "y" in list1:
		if "g" in list1:
			if "d" in list1:
				# if "y" in list1:
				print(word)

print("end")