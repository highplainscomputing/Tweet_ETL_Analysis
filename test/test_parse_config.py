from tweet_analyzer.utils.parse_config import parse_config
from tweet_analyzer.models.sentiment_classifier import TextClassifier



def test_parse_config():
    cfg = parse_config('config.yaml')
    assert isinstance(cfg, dict)
    assert len(cfg) > 0


def test_text_classifier_from_config():
    cfg = parse_config('config.yaml')
    text_classifier = TextClassifier.from_config(cfg)
    assert isinstance(text_classifier, TextClassifier)

