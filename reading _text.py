from sys import argv

def main():

    filename = argv[1]
    english = argv[2]
    f = open(filename)
    d = open(english)
    text = f.read()
    eng = d.read()
    listed_sentence = text.split(/n)
    common_word = eng.split()
    f.close()
    d.close()
    
    for line in listed_sentence:   
        c = check_dictionary(line, common_word)
        rest_program(c)

def check_dictionary_line(line, common_words):
    word_list = line.split()
    for i in range(len(word_list)):
        if word_list[0] not in common_words:
            ch

    for each_word in word_list:
        if each_word not in common_words:
            line.append(word_list)   

word_list = [] 

def rest_program(word_list)







main()