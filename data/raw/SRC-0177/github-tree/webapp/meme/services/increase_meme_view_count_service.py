from django.contrib.auth import get_user_model
from django.db import transaction
from meme.models import Meme

User = get_user_model()


class IncreaseMemeViewCountService:
    def __init__(self, meme: Meme, user: User):
        self.meme = meme
        self.user = user
        self.meme_counter = self.meme.meme_counter
        self.meme_view = None

    @transaction.atomic()
    def perform(self):
        if self.user.is_anonymous:  # NOTE: 익명 유저의 조회수를 어떻게 처리할 것인가?
            return
        meme_view_created = self.create_or_update_meme_view()
        self.increase_meme_view_count()

        if meme_view_created:
            self.increase_viewer_count()

    def create_or_update_meme_view(self) -> bool:
        self.meme_view, created = self.meme.meme_views.get_or_create(user=self.user)
        return created

    def increase_meme_view_count(self):
        self.meme_counter.views_count += 1
        self.meme_counter.save()

    def increase_viewer_count(self):
        self.meme_counter.viewers_count += 1
        self.meme_counter.save()
