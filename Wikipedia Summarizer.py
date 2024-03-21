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
from nltk.stem import PorterStemmer
from collections import Counter
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

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

    # Tokenization and Preprocessing
    sentences = sent_tokenize(content)
    stopWords = stopwords.words("english")
    ps = PorterStemmer()

    preprocessedSentences = []
    for sentence in sentences:
        preprocessedSentence = re.sub(r'\[[0-9]*\]', ' ', sentence)
        preprocessedSentence = re.sub(r'\s+', ' ', preprocessedSentence)
        preprocessedSentence = re.sub('[^a-zA-Z]', ' ', preprocessedSentence)
        preprocessedSentence = re.sub(r'\s+', ' ', preprocessedSentence)
        words = word_tokenize(sentence.lower())
        words = [ps.stem(word) for word in words if word.isalnum() and word not in stopWords]
        preprocessedSentences.append(words)
    
    # Train word embeddings
    model = Word2Vec(preprocessedSentences, vector_size = 300, window = 5, min_count = 1, workers = 6)

    # Compute sentence embeddings
    sentenceEmbeddings = []
    for sent in preprocessedSentences:
        sentEmbedding = [model.wv[word] for word in sent if word in model.wv]
        if sentEmbedding:
            sentenceEmbeddings.append(sum(sentEmbedding) / len(sentEmbedding))
        else:
            # If no word found in vocabulary, use zero vector
            sentenceEmbeddings.append([0] * 100)
    
    # Calculate sentence similarity using cosine similarity
    similarityMatrix = cosine_similarity(sentenceEmbeddings)

    # LexRank algorithm to rank sentences
    scores = [sum(similarityMatrix[i]) for i in range(len(similarityMatrix))]

    # Select top N sentences based on scores
    topSentences = sorted(range(len(scores)), key = lambda i: scores[i], reverse = True)[:summaryLength]
    summaryContent = [sentences[i] for i in topSentences]

    # Print the summary
    summaryContentOutput.setText(" ".join(summaryContent))

    # Most occurring words
    # Word Frequency Calculation
    wordFrequencies = Counter(word for word in word_tokenize(formattedContent) if word not in stopWords)
    # Sorting
    sortedWordFrequencies = sorted(wordFrequencies.items(), key = lambda item: item[1], reverse = True)
    topWords = sortedWordFrequencies[:13]
    # Populating the table
    for i, (topWord, frequency) in enumerate(topWords):
        frequencyItem = QTableWidgetItem(str(frequency))
        frequencyItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        topWordsTable.setItem(i, 0, QTableWidgetItem(topWord))
        topWordsTable.setItem(i, 1, frequencyItem)

wikipediaSummarizer = QApplication([])

# Create a window
window = QMainWindow()
window.setWindowTitle("Wikipedia Summarizer")
window.setGeometry(0, 0, 1600, 900)
window.setFixedSize(1600, 900)

# Font Attributes
font = QFont("Courier")
font.setPixelSize(18)
headerFont = QFont("Courier")
headerFont.setPixelSize(18)
headerFont.setBold(True)

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
summaryLengthLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
summaryContentOutput.setAlignment(Qt.AlignmentFlag.AlignJustify)
summaryContentOutput.setReadOnly(True)

# Top Words Table
topWordsTable = QTableWidget(13, 2, window)
topWordsTable.setFixedSize(400, 400)
topWordsTable.move(750, 50)
topWordsTable.setFont(font)
topWordsTable.horizontalHeader().setFont(headerFont)
topWordsTable.setHorizontalHeaderLabels(["Word", "Frequency"])
topWordsTable.setColumnWidth(0, 184)
topWordsTable.setColumnWidth(1, 184)
topWordsTable.resizeRowsToContents()

window.show()

wikipediaSummarizer.exec()