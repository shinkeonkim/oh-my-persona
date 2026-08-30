from django.test import TestCase

from matchmakings.models import CompatibilityTag


class CompatibilityTagModelTest(TestCase):
    """CompatibilityTag 모델 테스트"""

    def test_create_compatibility_tag_success(self):
        """CompatibilityTag가 정상적으로 생성되는지 테스트"""
        tag = CompatibilityTag.objects.create(name="성격이 잘 맞아요")

        self.assertIsNotNone(tag.id)
        self.assertEqual(tag.name, "성격이 잘 맞아요")

    def test_compatibility_tag_name_max_length(self):
        """CompatibilityTag의 name 필드가 최대 길이를 지원하는지 테스트"""
        long_name = "a" * 255
        tag = CompatibilityTag.objects.create(name=long_name)

        self.assertEqual(tag.name, long_name)
        self.assertEqual(len(tag.name), 255)

    def test_multiple_compatibility_tags(self):
        """여러 CompatibilityTag를 생성할 수 있는지 테스트"""
        tag1 = CompatibilityTag.objects.create(name="취미가 비슷해요")
        tag2 = CompatibilityTag.objects.create(name="가치관이 비슷해요")
        tag3 = CompatibilityTag.objects.create(name="성격이 보완적이에요")

        tags = CompatibilityTag.objects.all()
        self.assertEqual(tags.count(), 3)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        self.assertIn(tag3, tags)

    def test_compatibility_tag_update(self):
        """CompatibilityTag를 업데이트할 수 있는지 테스트"""
        tag = CompatibilityTag.objects.create(name="원래 이름")

        tag.name = "변경된 이름"
        tag.save()

        tag.refresh_from_db()
        self.assertEqual(tag.name, "변경된 이름")

    def test_compatibility_tag_delete(self):
        """CompatibilityTag를 삭제할 수 있는지 테스트"""
        tag = CompatibilityTag.objects.create(name="삭제할 태그")
        tag_id = tag.id

        tag.delete()

        self.assertFalse(CompatibilityTag.objects.filter(id=tag_id).exists())

    def test_compatibility_tag_filter_by_name(self):
        """CompatibilityTag를 이름으로 필터링할 수 있는지 테스트"""
        CompatibilityTag.objects.create(name="태그1")
        CompatibilityTag.objects.create(name="태그2")
        CompatibilityTag.objects.create(name="태그3")

        tag = CompatibilityTag.objects.filter(name="태그2").first()
        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, "태그2")

    def test_compatibility_tag_ordering(self):
        """CompatibilityTag를 정렬할 수 있는지 테스트"""
        tag1 = CompatibilityTag.objects.create(name="C 태그")
        tag2 = CompatibilityTag.objects.create(name="A 태그")
        tag3 = CompatibilityTag.objects.create(name="B 태그")

        ordered_tags = CompatibilityTag.objects.all().order_by("name")
        self.assertEqual(ordered_tags[0].id, tag2.id)  # A
        self.assertEqual(ordered_tags[1].id, tag3.id)  # B
        self.assertEqual(ordered_tags[2].id, tag1.id)  # C

    def test_compatibility_tag_count(self):
        """CompatibilityTag의 개수를 셀 수 있는지 테스트"""
        initial_count = CompatibilityTag.objects.count()

        CompatibilityTag.objects.create(name="새 태그 1")
        CompatibilityTag.objects.create(name="새 태그 2")

        final_count = CompatibilityTag.objects.count()
        self.assertEqual(final_count, initial_count + 2)

    def test_compatibility_tag_empty_name_allowed(self):
        """CompatibilityTag의 name이 빈 문자열로 생성 가능한지 테스트"""
        # CharField는 기본적으로 빈 문자열을 허용함
        tag = CompatibilityTag.objects.create(name="")

        self.assertIsNotNone(tag.id)
        self.assertEqual(tag.name, "")

        # 실제로 빈 문자열 태그가 저장되었는지 확인
        tag.refresh_from_db()
        self.assertEqual(tag.name, "")
