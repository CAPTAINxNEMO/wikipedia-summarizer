from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

# Sample text
text = open("sample.txt", encoding = "utf-8").read()

# Tokenize text into sentences
sentences = sent_tokenize(text)

# Tokenize and preprocess each sentence
stop_words = set(stopwords.words('english'))
ps = PorterStemmer()

preprocessed_sentences = []
for sentence in sentences:
    words = word_tokenize(sentence.lower())
    words = [ps.stem(word) for word in words if word.isalnum() and word not in stop_words]
    preprocessed_sentences.append(words)

# Train or load pre-trained word embeddings
# Example: Using Word2Vec
word2vec_model = Word2Vec(preprocessed_sentences, vector_size=200, window=5, min_count=1, workers=5)

# Compute sentence embeddings
sentence_embeddings = []
for sent in preprocessed_sentences:
    sent_embedding = [word2vec_model.wv[word] for word in sent if word in word2vec_model.wv]
    if sent_embedding:
        sentence_embeddings.append(sum(sent_embedding) / len(sent_embedding))
    else:
        sentence_embeddings.append([0] * 100)  # If no word found in vocabulary, use zero vector

# Calculate sentence similarity using cosine similarity
similarity_matrix = cosine_similarity(sentence_embeddings)

# LexRank algorithm to rank sentences
scores = [sum(similarity_matrix[i]) for i in range(len(similarity_matrix))]

# Select top sentences based on scores
top_sentences_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]  # Select top 3 sentences
summary = [sentences[i] for i in top_sentences_indices]

# Print the summary
print("\n".join(summary))