import string
import pandas as pd
import pymongo
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score


# Connect to DB
client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["msds696"]
mycol = mydb["climate_score_corpus"]

## TRAINING
# Load results into DataFrame
results = mycol.find()
df =  pd.DataFrame(list(results))
del df['_id']
df = df[df.label != 'Test']

# Data cleaning
def clean_text(corpus):
    tokens = word_tokenize(corpus)
    tokens = [w.lower() for w in tokens]
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    words = [word for word in stripped if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if not w in stop_words]
    words = ' '.join(words)

    return words

df['corpus_cleaned'] = df['corpus'].apply(clean_text)

y_hat = df['label'].tolist()
corpora = np.array(df['corpus_cleaned'].tolist())

count_vect = CountVectorizer()
x_train_counts = count_vect.fit_transform(corpora)

tfidf_transformer = TfidfTransformer()
x_train_tfidf = tfidf_transformer.fit_transform(x_train_counts)

train_x, test_x, train_y, test_y = train_test_split(x_train_tfidf, y_hat, test_size = 0.25, stratify = y_hat, random_state = 42)

clf = MultinomialNB().fit(train_x, train_y)

print(cross_val_score(clf, train_x, train_y, cv=5))

y_score = clf.predict(test_x)

n_right = 0
for i in range(len(y_score)):
    if y_score[i] == test_y[i]:
        n_right += 1

print("Training Stage Accuracy: %.2f%%" % ((n_right/float(len(test_y)) * 100)))

## TEST ON NEW NAMES

results = mycol.find()
df2 =  pd.DataFrame(list(results))
del df2['_id']
df2 = df2[df2.label == 'Test']

df2['corpus_cleaned'] = df2['corpus'].apply(clean_text)
corpora = np.array(df2['corpus_cleaned'].tolist())

x_test_counts = count_vect.transform(corpora)

x_test = tfidf_transformer.transform(x_test_counts)

df2['pred_class'] = clf.predict(x_test)
print(df2[['name','pred_class']])
