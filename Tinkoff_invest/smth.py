with open('figis.txt', encoding='utf-8') as f:
    t = f.readlines()
    for i in t:
        row = i.strip()
        counter = 0
        for letter in range(len(row)):
            if str(row[letter]) == ' ' and counter == 0:
                counter +=1
                print(row[:letter+1] + '*' + row[letter+1: ])