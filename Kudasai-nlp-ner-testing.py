import MeCab
import os
import spacy

tagger = MeCab.Tagger('-Ochasen') ## tokenizer
nlp = spacy.load("ja_core_news_md") ## NER basically applied NLP

i, ii = 0, 0

instanceCount = 0
nameCount = 0
nerCount = 0

iTotal = 0
meTotal = 0
nerTotal = 0

testChars = ["恵","学","久","澪","池","心","京","隼","夢","森","雅","翼","翔","颯","健","橘","茜","椿","陸","王","藪"] ## test characters
testCharnames = ["Kei","Manabu","Hisashi","Mio","Ike","Kokoro","Kyou","Hayato","Yume","Mori","Miyabi","Tsubasa","Kakeru","Sou","Ken","Tachibana","Akane","Tsubaki","Riku","Wan","Yabu"]

testCharInstanceCount = []
testCharNameCount = []
testCharNERCount = []

with open(r'C:\Users\Tetra\Desktop\vol 9 raw.txt', 'r+', encoding='utf-8') as file:  ## test file
    japText = file.readlines()


while(i < len(testChars)):
    while(ii < len(japText)):
        if(testChars[i] in japText[ii]):
            instanceCount += 1

            result = tagger.parse(japText[ii])

            lines = result.split('\n')

            for line in lines:
                if line != 'EOS':
                    parts = line.split('\t')
                    if len(parts) >= 4 and parts[0] == testChars[i] and (parts[3][:2] == '名詞' or parts[3] == '固有名詞') and parts[3][2:] not in ['副詞可能', '形容動詞語幹', '数']:
                        nameCount += 1

            doc = nlp(japText[ii])

            for ent in doc.ents:
                if ent.text == testChars[i] and ent.label_ == "PERSON":
                    nerCount += 1 
        ii += 1

    testCharInstanceCount.append(instanceCount)
    testCharNameCount.append(nameCount)
    testCharNERCount.append(nerCount)
    instanceCount = 0
    nameCount = 0
    nerCount = 0

    i += 1
    ii = 0

i = 0

while(i < len(testChars)):
    print("\n-----------------------------------------\nNum of " + testCharnames[i] + "-" + testChars[i] + " Occurrences : " + str(testCharInstanceCount[i]) + "\nNum of Occurrences Flagged as Names by MeCab : " + str(testCharNameCount[i]) + "\nNum of Occurrences Flagged as Names by SpaCy : " + str(testCharNERCount[i]) + "\n-----------------------------------------")
    iTotal += testCharInstanceCount[i]
    meTotal += testCharNameCount[i]
    nerTotal += testCharNERCount[i]
    i += 1

print("\nTotal Instances: " + str(iTotal))
print("Total Names: by MeCab : " + str(meTotal))
print("Total Names by SpaCy : " + str(nerTotal))

print("\n")
os.system('pause')
