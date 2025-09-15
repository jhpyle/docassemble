import os
import nltk
if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'omw-1.4.zip')):
    nltk.download('omw-1.4')
if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'wordnet.zip')):
    nltk.download('wordnet')
if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'wordnet_ic.zip')):
    nltk.download('wordnet_ic')
if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'sentiwordnet.zip')):
    nltk.download('sentiwordnet')
