
from abc import ABC, abstractmethod


class BaseModel(ABC):
    """
    An abstract base class that defines a template
    for inference through our other sub modules like Classifier,
    etc
    """

    @abstractmethod
    def apply(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.apply(*args, **kwargs)
