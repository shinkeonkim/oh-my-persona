from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import DataError, IntegrityError
from django.test import TestCase

import pytest

from users.choices import GenderChoice
from users.models import Child

User = get_user_model()


class ChildModelTests(TestCase):
    """Child 모델 테스트"""

    def setUp(self):
        """테스트용 사용자 생성"""
        self.parent = User.objects.create_user(
            username="parent123",
            password="password123",
        )

    def test_create_child_with_valid_data(self):
        """유효한 데이터로 자녀 생성"""
        child = Child.objects.create(
            parent=self.parent,
            name="홍길동",
            birth_year=2015,
            gender=GenderChoice.MALE,
        )
        self.assertEqual(child.name, "홍길동")
        self.assertEqual(child.birth_year, 2015)
        self.assertEqual(child.gender, GenderChoice.MALE)
        self.assertEqual(child.parent, self.parent)

    def test_child_has_one_to_one_relationship_with_parent(self):
        """자녀와 부모의 OneToOne 관계 확인"""
        child = Child.objects.create(
            parent=self.parent,
            name="홍길순",
            birth_year=2018,
            gender=GenderChoice.FEMALE,
        )
        # parent.child는 child 객체를 반환해야 함
        self.assertEqual(self.parent.child, child)
        self.assertEqual(child.parent, self.parent)

    def test_child_with_different_genders(self):
        """다양한 성별로 자녀 생성"""
        # 남자
        child_male = Child.objects.create(
            parent=self.parent,
            name="남자아이",
            birth_year=2010,
            gender=GenderChoice.MALE,
        )
        self.assertEqual(child_male.gender, GenderChoice.MALE)

        # 여자
        parent2 = User.objects.create_user(
            username="parent2",
            password="password123",
        )
        child_female = Child.objects.create(
            parent=parent2,
            name="여자아이",
            birth_year=2012,
            gender=GenderChoice.FEMALE,
        )
        self.assertEqual(child_female.gender, GenderChoice.FEMALE)

        # 선택 안함
        parent3 = User.objects.create_user(
            username="parent3",
            password="password123",
        )
        child_no_choice = Child.objects.create(
            parent=parent3,
            name="선택안함아이",
            birth_year=2014,
            gender=GenderChoice.NO_CHOICE,
        )
        self.assertEqual(child_no_choice.gender, GenderChoice.NO_CHOICE)

    def test_child_birth_year_minimum_value(self):
        """생년 최소값 검증 (1900)"""
        # 유효한 생년 (1900 이상)
        child = Child.objects.create(
            parent=self.parent,
            name="테스트",
            birth_year=1900,
            gender=GenderChoice.MALE,
        )
        self.assertEqual(child.birth_year, 1900)

        # 최신 생년
        child2 = Child.objects.create(
            parent=User.objects.create_user(username="parent2", password="pass123"),
            name="최신",
            birth_year=2024,
            gender=GenderChoice.MALE,
        )
        self.assertEqual(child2.birth_year, 2024)

    def test_child_name_max_length(self):
        """이름 최대 길이 (50자)"""
        # 경계값: 50자
        long_name = "가" * 50
        child = Child.objects.create(
            parent=self.parent,
            name=long_name,
            birth_year=2020,
            gender=GenderChoice.MALE,
        )
        self.assertEqual(len(child.name), 50)
        self.assertEqual(child.name, long_name)

    def test_child_name_over_max_length(self):
        """이름 최대 길이 초과 검증"""
        long_name = "가" * 51  # 51자리 (최대값 50초과)

        child = Child(
            parent=self.parent,
            name=long_name,
            birth_year=2020,
            gender=GenderChoice.MALE,
        )

        with pytest.raises(ValidationError):
            child.full_clean()

        with pytest.raises(DataError):
            child.save()

    def test_multiple_parents_with_children(self):
        """여러 부모가 각각 자녀를 가질 수 있음"""
        parent1 = User.objects.create_user(username="parent1", password="pass123")
        parent2 = User.objects.create_user(username="parent2", password="pass123")
        parent3 = User.objects.create_user(username="parent3", password="pass123")

        child1 = Child.objects.create(
            parent=parent1,
            name="아이1",
            birth_year=2010,
            gender=GenderChoice.MALE,
        )
        child2 = Child.objects.create(
            parent=parent2,
            name="아이2",
            birth_year=2011,
            gender=GenderChoice.FEMALE,
        )
        child3 = Child.objects.create(
            parent=parent3,
            name="아이3",
            birth_year=2012,
            gender=GenderChoice.NO_CHOICE,
        )

        self.assertEqual(parent1.child, child1)
        self.assertEqual(parent2.child, child2)
        self.assertEqual(parent3.child, child3)

        # 각 부모는 고유한 자녀를 가짐
        self.assertNotEqual(parent1.child, parent2.child)
        self.assertNotEqual(parent2.child, parent3.child)

    def test_parent_deletion_cascades_to_child(self):
        """부모 삭제 시 자녀도 함께 삭제됨 (CASCADE)"""
        child = Child.objects.create(
            parent=self.parent,
            name="삭제될아이",
            birth_year=2020,
            gender=GenderChoice.MALE,
        )

        child_id = child.id
        self.assertTrue(Child.objects.filter(id=child_id).exists())

        # 부모 삭제
        self.parent.delete()

        # 자녀도 삭제되어야 함
        self.assertFalse(Child.objects.filter(id=child_id).exists())

    def test_child_with_special_characters_in_name(self):
        """특수문자와 영문이 포함된 이름"""
        # 영문 포함
        child = Child.objects.create(
            parent=self.parent,
            name="김Tom",
            birth_year=2020,
            gender=GenderChoice.MALE,
        )
        self.assertEqual(child.name, "김Tom")

        # 공백 포함
        child2 = Child.objects.create(
            parent=User.objects.create_user(username="parent2", password="pass123"),
            name="홍 길 동",
            birth_year=2021,
            gender=GenderChoice.FEMALE,
        )
        self.assertEqual(child2.name, "홍 길 동")

    def test_child_creation_without_required_fields(self):
        """필수 필드 없이 자녀 생성 시도"""
        # name이 빈 문자열인 경우 - 데이터베이스는 허용하지만 검증에서 실패해야 함
        child = Child(
            parent=self.parent,
            name="",
            birth_year=2020,
            gender=GenderChoice.MALE,
        )
        # full_clean()을 호출하면 ValidationError가 발생해야 함
        with pytest.raises(ValidationError):
            child.full_clean()

        # birth_year가 None인 경우 - 데이터베이스 레벨에서 IntegrityError 발생
        with pytest.raises(IntegrityError):
            child = Child.objects.create(
                parent=User.objects.create_user(username="test2", password="pass123"),
                name="테스트",
                birth_year=None,
                gender=GenderChoice.MALE,
            )

    def test_child_default_gender(self):
        """기본 성별 값 (NO_CHOICE)"""
        child = Child.objects.create(
            parent=self.parent,
            name="기본값테스트",
            birth_year=2020,
        )
        self.assertEqual(child.gender, GenderChoice.NO_CHOICE)
