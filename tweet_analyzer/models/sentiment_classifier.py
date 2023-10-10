from typing import Dict, Any
from transformers import pipeline

from tweet_analyzer.models.base import BaseModel


class TextClassifier(BaseModel):
    def __init__(self, model_name: str, task: str):
        """Performs deep-learning-based sentiemnt Classification on Text Input.

        Based on: https://huggingface.co/transformers/

        Args:
            model_name: Path to the pre-trained bert models.
            task: Type of NLP task to be initialized.

        """
        
        self._classifier = pipeline(model=model_name)

    @staticmethod
    def from_config(config: Dict[str, Any]) -> 'TextClassifier':
        """Creates TextClassifier instance from a given config.

        Args
            config: Dictionary that contains project config.
                Expected fields:
                    args: Arguments for current TextClassifier constructor.

        Returns:
            TextClassifier instance.

        Raises:
            KeyError: In case of missing config fields.
            TypeError: In case of missing or wrong keyword arguments defined in `args`.
        """
        if 'sentiment_classifier' not in config:
            raise KeyError(f'Expects to have `sentiment_classifier` in config dictionary.')

        args = config['sentiment_classifier'].get('args', {})
        try:
            return TextClassifier(**args)
        except TypeError as e:
            raise TypeError(f'{e}. Check `args` fields defined in config with the actual keyword args'
                            f'required in {TextClassifier.__name__} `__init__` method.')

    def apply(self, sequence_to_classify: str) -> str:
        """Performs Classification on text input.

        Args:
            sequence_to_classify: Input Text for inference.

        Returns:
            category with highest probability.
        """

        output = self._classifier(sequence_to_classify)
        output = [sentiment['label'].title() for sentiment in output]
        
        return output
