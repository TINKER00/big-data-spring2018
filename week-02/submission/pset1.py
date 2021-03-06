##############################################################
 #### A. Lists ####
##############################################################

#A.1 Create a list containing any 4 strings
favorite_fruits = ["orange", "bananas", "melon", "pineapple"]
print favorite_fruits
# correct verion: print(favorite_fruits)
'''
Ariana, are you working in Python 2 by any chance? Python 3 requires you to put parentheses in a print statement, but you are mostly leaving them out here. If you are in Python 2, I'd recommend switching to Python 3 for this class.
'''

#A.2 Print the 3rd item in the list - remember how Python indexes lists!
print favorite_fruits[2]
# correct verion: print(favorite_fruits[2])
#A.3 Print the 1st and 2nd item in the list using [:] index slicing.
print favorite_fruits[0:2]
# correct verion: print(favorite_fruits[0:2])
#A.4 Add a new string with text “last” to the end of the list and print the list.
last_element = "last"
favorite_fruits.append(last_element)
print(favorite_fruits)

#A.5 Get the list length and print it.
favorite_fruits_length = len(favorite_fruits)
print favorite_fruits_length
# correct verion: print(favorite_fruits_length)

#A.6 Replace the last item in the list with the string “new” and print
for i, v in enumerate(favorite_fruits) :
    favorite_fruits[i] = v.replace("last","new")
print favorite_fruits
# correct verion: print(favorite_fruits)



##############################################################
####B. Strings####
##############################################################

sentence_words = ['I', 'am', 'learning', 'Python', 'to', 'munge', 'large', 'datasets', 'and', 'visualize', 'them']
print sentence_words
# correct version: print(sentence_words)

#B.1 Convert the list into a normal sentence with join(), then print.
type(sentence_words)
s = " "
sentence_words_normal = s.join( sentence_words )
print sentence_words_normal
# correct version: print(sentence_words_normal)

#B.2 Reverse the order of this list using the .reverse() method, then print.
sentence_words.reverse()
print sentence_words
# correct version: print(sentence_words)

#B.3 Now user the .sort() method to sort the list using the default sort order.
sentence_words.sort()
print sentence_words
# correct version: print(sentence_words)


#B.4 Perform the same operation using the sorted() function.
#Provide a brief description of how the sorted() function differs from the .sort() method.
sorted(sentence_words)
print sentence_words

#Explanation
#sorted() is more flexible, as it works on strings but also on dictionaries, tuples, and other structures. It creates a new list from the old & returns the new one, sorted.
#.sort() modifies the list in place. Thus, is faster than sorted() because it doesn't have to create a copy.

#B.5 Extra Credit: Modify the sort to do a case case-insensitive alphabetical sort.
sentence_words_alphabet_sort = sorted(sentence_words, key=lambda x: x.lower())
print(sentence_words_alphabet_sort)


##############################################################
###C. Random Function###
##############################################################

#given example
from random import randint
num = randint(0, 10)
num
#using a Function

import random
def random_numbers():
    min = int(0)
    max = int(input("Select Maximum Number "))
    numbers = [random.randint(min, max)]
    print(numbers)

random_numbers()

''' great use of the input function! remember that the assignment asks for both a high number and low number, as well as the assert function to test the function. here is an example of such a function.
'''
def my_random(max, min = 0):
    return randint(min,max)
    assert(0 <= my_random(100) <= 100)
    assert(50 <= my_random(100, min = 50) <= 100)

print(my_random(10000))


##############################################################
###D. String Formatting Function###
##############################################################

def book_info(number, title):
    print("The number {} bestseller today is {}".format(number, title.capitalize()))

# Call function
book_info(1, "evicted")


##############################################################
#E. Password Validation Function#
##############################################################

import re

def validate_password():
    while True:
        password = raw_input("Enter a password: ")
        #password = input("Enter a password: ") ## you added an extra raw_ to the input function, which kept the function from working, but otherwise excellent job!
        if (len(password)<8 or len(password)>14):
            print("Password needs to be between 8-14 characters long")
        if len([x for x in password if x.isdigit()]) < 2:
            print("Make sure your password has 2 numbers in it")
        if password.islower():
            print("Your password must have at least 1 capital leter")
        elif re.search('[!,?,@,#,$,%,^,&,*,(,),-]',password) is None:
                    print("Your password must include a special character")
        else:
            print("Your password works!")
            break
validate_password()

##############################################################
#F. Exponentiation Function#
##############################################################

n = int(input("n value: "))
m = int(input("m value: "))

def exp(a, b):
    number = 1
    for i in range(b):
        number = multiply(number, a)
    return number

print(exp(n, m))

'''
Ariana, you're really close here. A few things: you should put the input functions inside of your exp function, not outside of it. Also, you are using multiply here like a function, but you haven't defined it as a function. See one way for doing this below, and let me know if you have any questions!
'''
def exp(x, y):
  ex = x
  for i in range(1,y): ex*=x
  return ex

exp(2,3)
## end of PH edits

##############################################################
#G. Extra Credit: Min and Max Functions
##############################################################

def my_maximum(iterable):
    iterable = iter(iterable)
    maximum = iterable.next()
    for i in iterable:
        if i > maximum:
            maximum = i
    return maximum

a = [12, 10, 5, 55, 24]
my_maximum(a)


def my_minimum(iterable):
    iterable = iter(iterable)
    minimum = iterable.next()
    for i in iterable:
        if i < minimum:
            minimum = i
    return minimum

a = [12, 10, 5, 55, 24]
my_minimum(a)

'''Ariana, you are super close on this one. Unfortunately, I'm getting an error message when I run your code. See below for a correct answer, and let us know if you have questions!
'''

def min(num_list):
  m = num_list[0]
  for i in num_list:
    if i < m:
      m = i
    else:
      continue
      return m

min(num_list)
def max(num_list):
  m = num_list[0]
  for in num_list:
    if i > m:
      m = i
    else:
      continue
      return m
