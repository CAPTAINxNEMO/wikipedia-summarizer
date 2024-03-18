# GUI
from PyQt6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QMainWindow
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Libraries for Web Scraping
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

# Libraries for Text Preprocessing and Summarization
import re
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

def summary():
    link = linkInput.text()
    summaryLength = int(summaryLengthInput.text())

    webData = urlopen(link)
    data = bs(webData, "lxml")

    title = data.find("span", class_ = "mw-page-title-main")
    pageTitle = title.text
    pageTitleOutput.setText(pageTitle)

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
    stopWords = stopwords.words("english")

    wordFrequencies = {}

    # Word Frequency Calculation
    for word in word_tokenize(formattedContent):
        if word not in stopWords:
            if word not in wordFrequencies.keys():
                # First occurrence of a word
                wordFrequencies[word] = 1
            else:
                # Subsequent occurrences of the word
                wordFrequencies[word] += 1
        maximumFrequency = max(wordFrequencies.values())

    wf = wordFrequencies.copy()
    
    # Normalization
    for word in wordFrequencies.keys():
        wordFrequencies[word] = (wordFrequencies[word] / maximumFrequency)

    sentenceScores = {}

    # Scoring Sentences
    for sentence in sentenceList:
        for word in word_tokenize(sentence.lower()):
            # Word is relevant for scoring
            if word in wordFrequencies.keys():
                if len(sentence.split(" ")) < 40:
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
    summaryContent = " ".join(selectedSentences)
    summaryContentOutput.setText(summaryContent)

    # Most occurring words
    # Sorting the dictionary
    sortedWordFrequencies = sorted(wf.items(), key = lambda item: item[1], reverse = True)
    topWords = sortedWordFrequencies[:15]
    # Populating the table
    for i, (topWord, frequency) in enumerate(topWords):
        topWordsTable.setItem(i, 0, QTableWidgetItem(topWord))
        topWordsTable.setItem(i, 1, QTableWidgetItem(str(frequency)))
        topWordsTable.setColumnWidth(i, 175)
        topWordsTable.setRowHeight(i, 25)

wikipediaSummarizer = QApplication([])

# Create a window
window = QMainWindow()
window.setWindowTitle("Wikipedia Summarizer")
window.setGeometry(50, 50, 1600, 900)
window.setFixedSize(1600, 900)

# Font Attributes
font = QFont("Courier")
font.setPixelSize(18)

# Link Label
linkLabel = QLabel("Link", window)
linkLabel.setFixedSize(100, 50)
linkLabel.move(50, 50)
linkLabel.setFont(font)
linkLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

# Link Input
linkInput = QLineEdit(window)
linkInput.setFixedSize(550, 50)
linkInput.move(150, 50)
linkInput.setFont(font)
linkInput.setAlignment(Qt.AlignmentFlag.AlignCenter)

# Summary length Label
summaryLengthLabel = QLabel("No. of sentences in the summary", window)
summaryLengthLabel.setFixedSize(350, 50)
summaryLengthLabel.move(50, 100)
summaryLengthLabel.setFont(font)
linkLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

# Summary length Input
summaryLengthInput = QLineEdit(window)
summaryLengthInput.setFixedSize(300, 50)
summaryLengthInput.move(400, 100)
summaryLengthInput.setFont(font)
summaryLengthInput.setAlignment(Qt.AlignmentFlag.AlignCenter)

# Summarize Button
summarize = QPushButton("Summarize", window)
summarize.setFixedSize(150, 50)
summarize.move(300, 150)
summarize.setFont(font)
summarize.clicked.connect(summary)

# Wikipedia page Title
pageTitleOutput = QLabel(window)
pageTitleOutput.setFixedSize(650, 50)
pageTitleOutput.move(50, 250)
pageTitleOutput.setFont(font)
pageTitleOutput.setAlignment(Qt.AlignmentFlag.AlignCenter)

# Summary Content
summaryContentOutput = QTextEdit(window)
summaryContentOutput.setFixedSize(650, 550)
summaryContentOutput.move(50, 300)
summaryContentOutput.setFont(font)
pageTitleOutput.setAlignment(Qt.AlignmentFlag.AlignJustify)
summaryContentOutput.setReadOnly(True)

# Top Words Table
topWordsTable = QTableWidget(15, 2, window)
topWordsTable.setFixedSize(400, 400)
topWordsTable.move(750, 50)
topWordsTable.setFont(font)
topWordsTable.setHorizontalHeaderLabels(["Word", "Frequency"])

window.show()

wikipediaSummarizer.exec()