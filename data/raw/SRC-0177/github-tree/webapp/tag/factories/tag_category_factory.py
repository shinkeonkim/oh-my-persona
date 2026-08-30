import factory
from factory.django import DjangoModelFactory
from tag.models.tag_category import TagCategory


class TagCategoryFactory(DjangoModelFactory):

    class Meta:
        model = TagCategory

    name = factory.Faker("word")
