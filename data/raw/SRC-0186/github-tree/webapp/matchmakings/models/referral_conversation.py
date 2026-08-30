from django.db import models

from common.models import BaseModel

from .referral import Referral


class ReferralConversation(BaseModel):

  class Meta:
    db_table = "referral_conversations"
    verbose_name = "Referral Conversation"
    verbose_name_plural = "Referral Conversations"

  referral = models.OneToOneField(
    Referral,
    on_delete=models.CASCADE,
    related_name="conversation",
    verbose_name="추천",
  )
  conversation_messages = models.JSONField(
    verbose_name="대화 메시지",
    help_text="ConversationMessage 형태의 대화 메시지 리스트",
  )
  opposite_conversation_messages = models.JSONField(
    verbose_name="호감을 받는 사람에게 노출할 대화 메시지",
    help_text="ConversationMessage 형태의 대화 메시지 리스트",
    default=list,
  )

  def __str__(self):
    return f"Conversation for {self.referral}"
