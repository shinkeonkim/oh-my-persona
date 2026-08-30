from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from meme.models import Meme
from tag.models import Tag, TagCategory

User = get_user_model()


class MemeModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )

        self.tag_category = TagCategory.objects.create(name="test")
        self.tag1 = Tag.objects.create(
            name="Funny", first_letter="F", category=self.tag_category
        )
        self.tag2 = Tag.objects.create(
            name="Animals", first_letter="A", category=self.tag_category
        )
        self.tag3 = Tag.objects.create(
            name="Sports", first_letter="S", category=self.tag_category
        )

        self.meme1 = Meme.objects.create(
            type="Image",
            title="First Meme",
            description="First meme description",
            creator=self.user,
            published_at=timezone.now(),
        )
        self.meme1.tags.set([self.tag1, self.tag2])

        self.meme2 = Meme.objects.create(
            type="Video",
            title="Second Meme",
            description="Second meme description",
            creator=self.user,
            published_at=None,
        )
        self.meme2.tags.set([self.tag2, self.tag3])

        self.meme3 = Meme.objects.create(
            type="Audio",
            title="Third Meme",
            description="Third meme description",
            creator=self.user,
            archived_at=timezone.now(),
        )
        self.meme3.tags.set([self.tag1, self.tag3])

    def test_meme_instance_creation(self):
        meme = Meme.objects.get(title="First Meme")
        self.assertEqual(meme.type, "Image")
        self.assertEqual(meme.creator, self.user)
        self.assertTrue(meme.published_at is not None)

    def test_queryset_methods(self):
        self.assertEqual(Meme.objects.published().count(), 1)
        self.assertEqual(Meme.objects.preparing().count(), 1)
        self.assertEqual(Meme.objects.active().count(), 2)
        self.assertEqual(Meme.objects.archived().count(), 1)

    def test_related_memes(self):
        related_to_meme1 = list(self.meme1.related_memes)
        self.assertEqual(len(related_to_meme1), 2)
        self.assertIn(self.meme2, related_to_meme1)
        self.assertIn(self.meme3, related_to_meme1)

        # 가장 태그가 많이 겹치는 meme2 확인
        self.assertEqual(related_to_meme1[0], self.meme2)
        self.assertEqual(related_to_meme1[0].common_tags_count, 1)

    def test_meme_counters(self):
        meme = self.meme1
        self.assertIsNotNone(meme.meme_counter)

    def test_publish_and_archive_methods(self):
        meme = Meme.objects.create(
            type="Text",
            title="Draft Meme",
            description="Draft meme description",
            creator=self.user,
        )

        self.assertIsNone(meme.published_at)

        meme.publish()
        self.assertIsNotNone(meme.published_at)

        meme.undo_publish()
        self.assertIsNone(meme.published_at)

        meme.archive()
        self.assertIsNotNone(meme.archived_at)

        meme.undo_archive()
        self.assertIsNone(meme.archived_at)
