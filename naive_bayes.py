import pandas as pd
import pymongo
from nltk.tokenize import word_tokenize
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import cross_val_score

# Connect to DB
client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["msds696"]
mycol = mydb["climate_score_corpus"]

# Load results into DataFrame
results = mycol.find()
df =  pd.DataFrame(list(results))
del df['_id']
df = df[df.label != 'Test']

y_hat = df['label'].tolist()
corpora = np.array(df['corpus'].tolist())

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

print("Accuracy: %.2f%%" % ((n_right/float(len(test_y)) * 100)))
