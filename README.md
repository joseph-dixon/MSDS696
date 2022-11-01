# MSDS696

Climate change is the defining issue of our time and reducing U.S. emissions will require substantive policy change in the coming years. This will necessitate that the American electorate vote for climate-friendly politicians in upcoming election cycles. However, for many voters, it can be difficult to identify where a candidate stands on climate change.

This capstone seeks to solve that problem through web scraping, NLP, and machine learning. First, I define a dictionary of training data with three different labels: "climate_friendly", "climate_neutral", and "climate_hostile". Next, the application uses the Selenium library to scrape Google Search results for {Candidate Name} + "Climate" and returns the unstructured text corpus of the top 10 search results. This typically includes the candidate's own website, as well as recent news articles and opinion pieces about the candidate. The name, label, and corpora are stored in a local MongoDB database for later use.

The application then performs text cleaning on the corpora and trains two different ML models on the training data. These are a Naive Bayes model and a Convolutional Neural Network. In practice, the Naive Bayes model performed slightly better than the CNN.

Finally, the model can be supplied with new names/corpora and it will classify these new candidates into the categories described above.
