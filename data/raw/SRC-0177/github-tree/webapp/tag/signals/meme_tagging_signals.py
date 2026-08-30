from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from tag.models import MemeTagging
from tag.tasks.tag_counter_tasks import update_counters_for_tag


@receiver(post_save, sender=MemeTagging)
def update_tag_counter_on_meme_tagging_save(sender, instance, **kwargs):
    """
    밈 태깅이 저장될 때 관련 태그 카운터 업데이트
    """
    if instance.tag:
        update_counters_for_tag.delay(instance.tag.id)


@receiver(post_delete, sender=MemeTagging)
def update_tag_counter_on_meme_tagging_delete(sender, instance, **kwargs):
    """
    밈 태깅이 삭제될 때 관련 태그 카운터 업데이트
    """
    if instance.tag:
        update_counters_for_tag.delay(instance.tag.id)
