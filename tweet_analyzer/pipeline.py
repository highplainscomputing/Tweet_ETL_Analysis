"""
Defines end-to-end pipeline that extracts a tweet,
transform and filter values and load them in MongoDB.
After that we fetch a tweet, perform sentiment analysis and emotion recognition on it
using pre-trained models from hugging-face    .

1. Put file with models class implementation into `models` module.
2. Import models class in `models/__init__.py` file.
"""
from typing import Dict, Any

from tweet_analyzer import logger
from tweet_analyzer import models


class Pipeline(models.BaseModel):
    def __init__(self, sentiment_analyzer: models.TextClassifier,emotion_analyzer: models.EmotionClassifier):
        """Performs Text Classification for the given text.

        Supported types of categories for can be defined at config.yaml.
        Pipeline performs the following steps:
        ```
        Classify the given text.

        Perform Emotion Analysis.

        TODO: Demographic Analysis.
        ```

        Args:
            post_classifier: `TextClassifier` instance.
            emotion_classifier: `TextClassifier` instance
            
        """
        self.post_classifier = sentiment_analyzer
        self.post_emotion_analyzer = emotion_analyzer

    @staticmethod
    def from_config(config: Dict[str, Any]) -> 'Pipeline':
        """Instantiates Pipeline object from config file."""
        pipeline = dict()
        pipeline['sentiment_classifier'] = models.TextClassifier.from_config(config)
        pipeline['emotion_analyzer'] = models.EmotionClassifier.from_config(config)
        logger.info('Pipeline has been configured with the following modules:')
        for name, module in pipeline.items():
            logger.info(f'  {name.replace("_", " ").title()}: {module}')

        return Pipeline(sentiment_analyzer=pipeline['sentiment_classifier'],
                        emotion_analyzer=pipeline['emotion_analyzer']
                        )

    def apply(self, post: str, task:str) -> Dict[str, Any]:
        """Runs end-to-end pipeline for the given text.

        Args:
            post: Social Media Post to process.

        Returns:
            Categories of Labels for Emotion and Sentiment Classification
        """
        return {
            "sentiment": self.post_classifier.apply(sequence_to_classify=post)} if task=="sentiment_classifier" else {
                "emotions": self.post_emotion_analyzer(sequence_to_classify=post)
                }
