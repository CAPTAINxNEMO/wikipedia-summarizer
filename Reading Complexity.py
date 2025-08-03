from urllib.request import urlopen
from bs4 import BeautifulSoup

from re import sub
from nltk import sent_tokenize
from nltk.corpus import stopwords
from spacy import load as spacy_load

from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

from numpy import mean, zeros, array

from textstat.backend.metrics import flesch_kincaid_grade, flesch_reading_ease, gunning_fog, smog_index, dale_chall_readability_score

link = 'https://en.wikipedia.org/wiki/Computer'
summaryLength = 7

try:
    webData = urlopen(link)
    data = BeautifulSoup(webData, 'lxml')

    title = data.find('span', class_ = 'mw-page-title-main')
    if title:
        pageTitle = title.text
    else:
        pageTitle = 'No Title Found'

    print(f'Page Title: {pageTitle}')

    paragraphs = data.find_all('p')
    content = ''
    for p in paragraphs:
        content += p.text

    content = sub(r'\[[0-9a-zA-Z]*\]', ' ', content)
    content = sub(r'\s+', ' ', content)
    content = sub(r'(?<=\d)(st|nd|rd|th)', '', content)
    content = sub(r'\s+', ' ', content)

    formattedContent = sub('[^a-zA-Z]', ' ', content)
    formattedContent = sub(r'\s+', ' ', formattedContent)

    stopWords = stopwords.words('english')
    spacyLoad = spacy_load('en_core_web_lg')
    sentences = sent_tokenize(content)

    preprocessedSentences = []
    for sentence in sentences:
        preprocessedSentence = sub(r'\[[0-9a-zA-Z]*\]', ' ', sentence)
        preprocessedSentence = sub(r'\s+', ' ', preprocessedSentence)
        preprocessedSentence = sub('[^a-zA-Z]', ' ', preprocessedSentence)
        preprocessedSentence = sub(r'\s+', ' ', preprocessedSentence)
        doc = spacyLoad(preprocessedSentence.lower())
        words = [token.lemma_ for token in doc if token.is_alpha and token.lemma_ not in stopWords]
        preprocessedSentences.append(words)

    model = Word2Vec(preprocessedSentences, vector_size = 300, window = 5, min_count = 4, workers = 6)

    sentenceEmbeddings = []
    for sent in preprocessedSentences:
        sentEmbedding = [model.wv[word] for word in sent if word in model.wv]
        if sentEmbedding:
            sentenceEmbeddings.append(mean(sentEmbedding, axis = 0))
        else:
            sentenceEmbeddings.append(zeros(model.vector_size))
    sentenceEmbeddingsArray = array(sentenceEmbeddings)

    similarityMatrix = cosine_similarity(sentenceEmbeddingsArray)
    scores = [sum(similarityMatrix[i]) for i in range(len(similarityMatrix))]
    topSentences = sorted(range(len(scores)), key = lambda i: scores[i], reverse = True)[:summaryLength]
    summaryContent = [sentences[i] for i in topSentences]
    summaryText = ' '.join(summaryContent)

    print(summaryText)

    print(f'\nFlesch Reading Ease:        {flesch_reading_ease(summaryText, 'en')}')
    print(f'Flesch-Kincaid Grade:         {flesch_kincaid_grade(summaryText, 'en')}')
    print(f'Gunning Fog:                  {gunning_fog(summaryText, 'en')}')
    print(f'SMOG Index:                   {smog_index(summaryText, 'en')}')
    print(f'Dale-Chall Readability Score: {dale_chall_readability_score(summaryText, 'en')}')
except Exception as e:
    pageTitle = f'Error: Unable to access page - {str(e)}'
