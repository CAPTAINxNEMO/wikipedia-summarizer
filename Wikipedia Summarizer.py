# Libraries for Web Scraping
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

# Libraries for Text Preprocessing and Summarization
import re
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import heapq

url = "https://en.wikipedia.org/wiki/SARS-CoV-2"
summaryLength = 7
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
            if len(sentence.split(' ')) < 40:
                # sentenceScore = sum(Normalized wordFrequencies of the words in the sentence)
                if sentence not in sentenceScores.keys():
                    # Sentence already in sentenceScores{}
                    sentenceScores[sentence] = wordFrequencies[word]
                else:
                    # Sentence not in sentenceScores{}
                    sentenceScores[sentence] += wordFrequencies[word]

# Summarization
# Top n sentences with the highest sentenceScores
sortedSentences = sorted(sentenceScores.items(), key = lambda x: x[1], reverse = True)
selectedSentences = []
for sentence, score in sortedSentences:
    if sentence in content:
        selectedSentences.append(sentence)
    if len(selectedSentences) == summaryLength:
        break
summary = " ".join(selectedSentences)
print(summary)