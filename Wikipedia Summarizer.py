# GUI
from tkinter import *

# Libraries for Web Scraping
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

# Libraries for Text Preprocessing and Summarization
import re
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import heapq

window = Tk()
window.title("Wikipedia Summarizer")
window.geometry("1280x720")
window.resizable(False, False)

# url = StringVar()
url = "https://en.wikipedia.org/wiki/SARS-CoV-2"
# summaryLength = StringVar()
summaryLength = 7

urlLabel = Label(window, text = "Wikipedia page link").place(x = 40, y = 60) 
summaryLengthLabel = Label(window, text = "Number of sentences in the summary").place(x = 40, y = 100)
urlInput = Entry(window, textvariable = url, width = 30).place(x = 300, y = 60)
summaryLengthInput = Entry(window, textvariable = summaryLength, width = 30).place(x = 300, y = 100)
submitButton = Button(window, text = "Submit").place(x = 40, y = 130)
summaryOutput = Text(window, height = 20, width = 52)

webData = urlopen(url)

data = bs(webData, "lxml")
paragraphs = data.find_all("p")

content = ""
for p in paragraphs:
    content += p.text

# Removing Square Brackets and Extra Spaces
content = re.sub(r'\[[0-9]*\]', ' ', content)
content = re.sub(r'\s+', ' ', content)
# Removing special characters and digits
formattedContent = re.sub('[^a-zA-Z]', ' ', content)
formattedContent = re.sub(r'\s+', ' ', formattedContent)

# Sentence Tokenization and Stopwords Removal
sentenceList = sent_tokenize(content)
stopwords = stopwords.words('english')

wordFrequencies = {}

# Word Frequency Calculation
for word in word_tokenize(formattedContent):
    if word not in stopwords:
        if word not in wordFrequencies.keys():
            # First occurrence of a word
            wordFrequencies[word] = 1
        else:
            # Subsequent occurrences of the word
            wordFrequencies[word] += 1
    maximumFrequency = max(wordFrequencies.values())

# Normalization (ensure all frequencies are between 0 to 1)
for word in wordFrequencies.keys():
    wordFrequencies[word] = (wordFrequencies[word] / maximumFrequency)

sentenceScores = {}

# Scoring Sentences
for sentence in sentenceList:
    for word in word_tokenize(sentence.lower()):
        # Word is relevant for scoring
        if word in wordFrequencies.keys():
            # Sentence longer than 30 words (too long)
            # if len(sentence.split(' ')) < 30:
            # sentenceScore = sum(Normalized wordFrequencies of the words in the sentence)
            if sentence not in sentenceScores.keys():
                # Sentence already in sentenceScores{}
                sentenceScores[sentence] = wordFrequencies[word]
            else:
                # Sentence not in sentenceScores{}
                sentenceScores[sentence] += wordFrequencies[word]

# Summarization
# Top n sentences with the highest sentenceScores
summarySentences = heapq.nlargest(summaryLength, sentenceScores, key = sentenceScores.get)
summary = " ".join(summarySentences)
print(summary)

summaryOutput.insert(END, summary)

window.mainloop()