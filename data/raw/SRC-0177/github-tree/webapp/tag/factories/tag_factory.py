import factory
from tag.models import Tag


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Faker("word")
    description = factory.Faker("text")
    category = factory.SubFactory("tag.factories.TagCategoryFactory")
