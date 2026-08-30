# webapp/factories/base.py
import factory
from faker import Faker

fake = Faker()


class BaseFactory(factory.django.DjangoModelFactory):
    """Base factory for all models inheriting from BaseModel."""

    class Meta:
        abstract = True


class TraitsMixin:
    """Mixin to define traits that can be applied to any factory."""

    @factory.post_generation
    def with_traits(self, create, extracted_traits, **kwargs):
        if not create:
            return

        if extracted_traits:
            for trait in extracted_traits:
                trait.apply(self, **kwargs)


class Trait:
    """Base class for defining traits that can be applied to model instances."""

    @classmethod
    def apply(cls, instance, **kwargs):
        raise NotImplementedError("Traits must implement apply() method")
