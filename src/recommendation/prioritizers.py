from urllib.parse import urlparse

import jieba
import numpy as np
from sklearn.base import TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline, FeatureUnion


class MapTransformer(TransformerMixin):
    def __init__(self, trans_impl):
        self.trans_impl = np.vectorize(trans_impl)

    def transform(self, X, **transform_params):
        return self.trans_impl(X)

    def fit(self, X, Y=None, **fit_params):
        return self


def isascii(string):
    try:
        string.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True


def extract_entry_features(entry):
    title = entry.title

    return {
        'feed': entry.feed.name,
        'domain': urlparse(entry.link).hostname,
        'author': entry.json.get('author', '__unknown__'),
        'content_length': len(entry.content),
        'title_length': len(title),
        'title_has_digit': any(map(str.isdigit, title)),
        'title_is_english': any(map(isascii, title)),
    }


def tokenize(value):
    tokens = jieba.cut(value)
    striped = (token.strip() for token in tokens)
    non_empty = (token for token in striped if token)
    lower = (token.lower() for token in non_empty)
    return list(lower)


def extract_tags(entry):
    tags = entry.json.get('tags')
    if not tags:
        return ()
    return [tag['term'].lower() for tag in tags]


@np.vectorize
def extract_entry(entry_state):
    return entry_state.entry


@np.vectorize
def extract_recommend(entry_state):
    return entry_state.opened or entry_state.starred


def extract_title(entry):
    return entry.title


def identity(x):
    return x


def build(entry_states):
    pipeline = Pipeline([
        ('features', FeatureUnion([
            ('title', Pipeline([
                ('extract_title', MapTransformer(extract_title)),
                ('vectorize', TfidfVectorizer(tokenizer=tokenize)),
            ])),
            ('entry', Pipeline([
                ('extract_feautres', MapTransformer(extract_entry_features)),
                ('vectorize', DictVectorizer()),
            ])),
            ('tags', Pipeline([
                ('vectorize', TfidfVectorizer(
                    preprocessor=identity,
                    tokenizer=extract_tags,
                )),
            ])),
        ])),
        ('classifier', MultinomialNB(fit_prior=True)),
    ])
    data = np.array(entry_states)
    entries = extract_entry(data)
    target = extract_recommend(data)
    classifier = pipeline.fit(entries, target)

    return NBPrioritizer(classifier)


class NBPrioritizer:
    def __init__(self, classifier):
        self.classifier = classifier

    def prioritize(self, entry):
        return self.classifier.predict_proba(np.array([entry]))[0][1]
