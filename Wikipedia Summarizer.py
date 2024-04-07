# GUI
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QRadioButton, QButtonGroup, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QFont, QPixmap
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
from gensim.models import Word2Vec, LdaModel
from gensim.corpora import Dictionary
from sklearn.metrics.pairwise import cosine_similarity

# Data Visualization
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

def summary():
    link = linkInput.text()
    # Summary Length
    selectedRadioButton = summaryLengthInputGroup.checkedButton().text()
    if selectedRadioButton == "Short":
        summaryLength = 4
    elif selectedRadioButton == "Medium":
        summaryLength = 7
    else:
        summaryLength = 10

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
    
    # Summary
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
    
    # WordCloud Generation
    wordcloud = WordCloud(height = 400, width = 400, background_color = "white", stopwords = stopWords).generate(formattedContent)
    plt.imshow(wordcloud, interpolation = "bilinear")
    plt.axis("off")
    wordcloud.to_file("wordcloud.png")
    wordcloudPixmap = QPixmap("wordcloud.png")
    wordCloudOutput.setPixmap(wordcloudPixmap)

    # Cluster Graph
    sentenceEmbeddingsArray = np.array(sentenceEmbeddings)
    # Number of Clusters
    silhouetteScores = []
    for k in range(2, 10):
        kmeans = KMeans(n_clusters = k, random_state = 42, n_init = 10)
        kmeans.fit(sentenceEmbeddings)
        score = silhouette_score(sentenceEmbeddingsArray, kmeans.labels_)
        silhouetteScores.append(score)
    numClusters = silhouetteScores.index(max(silhouetteScores)) + 2
    clusterLabels = kmeans.labels_
    # Perform dimensionality reduction using t-SNE
    tsne = TSNE(n_components = 2, random_state = 42)
    embeddedSentences = tsne.fit_transform(sentenceEmbeddingsArray)
    # Extract X and Y coordinates
    x = embeddedSentences[:, 0]
    y = embeddedSentences[:, 1]
    # Plot the clusters
    myDPI = 96
    plt.figure(figsize = (400 / myDPI, 400 / myDPI), dpi = myDPI)
    for clusterNum in range(numClusters):
        plt.scatter(x[clusterLabels == clusterNum], y[clusterLabels == clusterNum], label = f"Cluster {clusterNum + 1}")
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.legend()
    plt.title("t-SNE Visualization of Clusters")
    plt.savefig("clustering.png", format = "png")
    clusteringPixmap = QPixmap("clustering.png")
    clusteringGraphOutput.setPixmap(clusteringPixmap)

    # Topic Modelling
    numTopics = numClusters
    if numTopics < 5:
        numTopics = 5
    dictionary = Dictionary(preprocessedSentences)
    corpus = [dictionary.doc2bow(sent) for sent in preprocessedSentences]
    # Training the LDA Model
    ldaModel = LdaModel(corpus, num_topics = numTopics, id2word = dictionary, passes = 20)
    # Print the topics
    topics = ldaModel.print_topics(num_words = numTopics)
    topicModellings = []
    for topicIndex, topic in enumerate(topics):
        topicWords = [word for word, _ in ldaModel.show_topic(topicIndex)]
        topicModelling = f"Topic {topicIndex + 1}: {", ".join(topicWords)}"
        topicModellings.append(topicModelling)
    allTopicModellings = "\n\n".join(topicModellings)
    topicModellingOutput.setText(allTopicModellings)

wikipediaSummarizer = QApplication([])

# Create a window
window = QMainWindow()
window.setWindowTitle("Wikipedia Summarizer")
window.setGeometry(0, 0, 1600, 900)
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
linkInput.setStyleSheet('border: 1px solid black;')

# Summary length Label
summaryLengthLabel = QLabel("Summary Length", window)
summaryLengthLabel.setFixedSize(200, 50)
summaryLengthLabel.move(50, 100)
summaryLengthLabel.setFont(font)
summaryLengthLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

# Summary length Input
# Radio Buttons
summaryLengthShort = QRadioButton("Short", window)
summaryLengthShort.setFixedSize(150, 50)
summaryLengthShort.move(250, 100)
summaryLengthShort.setFont(font)
summaryLengthMedium = QRadioButton("Medium", window)
summaryLengthMedium.setFixedSize(150, 50)
summaryLengthMedium.move(400, 100)
summaryLengthMedium.setFont(font)
summaryLengthMedium.setChecked(True)
summaryLengthLong = QRadioButton("Long", window)
summaryLengthLong.setFixedSize(150, 50)
summaryLengthLong.move(550, 100)
summaryLengthLong.setFont(font)
# Grouping the buttons
summaryLengthInputGroup = QButtonGroup(window)
summaryLengthInputGroup.addButton(summaryLengthShort)
summaryLengthInputGroup.addButton(summaryLengthMedium)
summaryLengthInputGroup.addButton(summaryLengthLong)

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
pageTitleOutput.setStyleSheet('border: 1px solid black;')

# Summary Content
summaryContentOutput = QTextEdit(window)
summaryContentOutput.setFixedSize(650, 550)
summaryContentOutput.move(50, 300)
summaryContentOutput.setFont(font)
summaryContentOutput.setAlignment(Qt.AlignmentFlag.AlignJustify)
summaryContentOutput.setStyleSheet('border: 1px solid black;')
summaryContentOutput.setReadOnly(True)

# Top Words Table
topWordsTable = QTableWidget(13, 2, window)
topWordsTable.setFixedSize(400, 400)
topWordsTable.move(750, 50)
topWordsTable.setFont(font)
topWordsTable.horizontalHeader().setStyleSheet("QHeaderView::section {height: 34px; font-family: 'Courier'; font-size: 18px; font-weight: bold}")
topWordsTable.setHorizontalHeaderLabels(["Word", "Frequency"])
topWordsTable.setColumnWidth(0, 184)
topWordsTable.setColumnWidth(1, 184)
topWordsTable.resizeRowsToContents()

# WordCloud
wordCloudOutput = QLabel(window)
wordCloudOutput.setFixedSize(400, 400)
wordCloudOutput.move(1150, 50)
wordCloudOutput.setStyleSheet('border: 1px solid black;')

# Topic Modelling Label
topicModellingLabel = QLabel("Topic Modelling", window)
topicModellingLabel.setFixedSize(400, 50)
topicModellingLabel.move(750, 450)
topicModellingLabel.setFont(font)
topicModellingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
topicModellingLabel.setStyleSheet('border: 1px solid black;')

# Topic Modelling Output
topicModellingOutput = QTextEdit(window)
topicModellingOutput.setFixedSize(400, 350)
topicModellingOutput.move(750, 500)
topicModellingOutput.setFont(font)
topicModellingOutput.setAlignment(Qt.AlignmentFlag.AlignJustify)
topicModellingOutput.setStyleSheet('border: 1px solid black;')
topicModellingOutput.setReadOnly(True)

# Clustering Graph Output
clusteringGraphOutput = QLabel(window)
clusteringGraphOutput.setFixedSize(400, 400)
clusteringGraphOutput.move(1150, 450)
clusteringGraphOutput.setStyleSheet('border: 1px solid black;')

window.show()

wikipediaSummarizer.exec()