from bookmark.models import Bookmarking
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from tag.tasks.tag_counter_tasks import update_counters_for_user


@receiver(post_save, sender=Bookmarking)
def update_bookmarkings_count_on_save(sender, instance, created, **kwargs):
    if hasattr(instance, "bookmark") and instance.bookmark is not None:
        bookmark = instance.bookmark
        bookmark.reset_bookmarkings_count()
        user_id = bookmark.user.id
    else:
        user_id = instance.user.id

    if hasattr(instance, "meme") and instance.meme is not None:
        instance.meme.reset_all_counters()

    update_counters_for_user.delay(user_id)


@receiver(post_delete, sender=Bookmarking)
def update_bookmarkings_count_on_delete(sender, instance, **kwargs):
    if hasattr(instance, "bookmark") and instance.bookmark is not None:
        bookmark = instance.bookmark
        bookmark.reset_bookmarkings_count()
        user_id = bookmark.user.id
    else:
        user_id = instance.user.id

    if hasattr(instance, "meme") and instance.meme is not None:
        instance.meme.reset_all_counters()

    update_counters_for_user.delay(user_id)
