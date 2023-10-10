from typing import Dict, Any
from transformers import pipeline

from tweet_analyzer.models.base import BaseModel


class EmotionClassifier(BaseModel):
    def __init__(self, model_name: str, task: str):
        """Performs deep-learning-based sentiemnt Classification on Text Input.

        Based on: https://huggingface.co/transformers/

        Args:
            model_name: Path to the pre-trained bert models.
            task: Type of NLP task to be initialized.

        """
        
        self._classifier = pipeline(task=task,model=model_name,top_k=4)

    @staticmethod
    def from_config(config: Dict[str, Any]) -> 'EmotionClassifier':
        """Creates TextClassifier instance from a given config.

        Args
            config: Dictionary that contains project config.
                Expected fields:
                    args: Arguments for current TextClassifier constructor.

        Returns:
            EmotionClassifier instance.

        Raises:
            KeyError: In case of missing config fields.
            TypeError: In case of missing or wrong keyword arguments defined in `args`.
        """
        if 'emotion_analysis' not in config:
            raise KeyError(f'Expects to have `emotion_analysis` in config dictionary.')

        args = config['emotion_analysis'].get('args', {})
        try:
            return EmotionClassifier(**args)
        except TypeError as e:
            raise TypeError(f'{e}. Check `args` fields defined in config with the actual keyword args'
                            f'required in {EmotionClassifier.__name__} `__init__` method.')

    def apply(self, sequence_to_classify: str) -> str:
        """Performs Classification on text input.

        Args:
            sequence_to_classify: Input Text for inference.

        Returns:
            Emotion categories with highest probability.
        """

        outputs = self._classifier(sequence_to_classify)
        output = [output['label'].title() for output in outputs[0]]
        
        
        return output
