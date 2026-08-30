from django.db import models

from common.models import BaseModel
from saju.choices import BranchChoice, StemChoice


class PreparedCompatibilityTag(BaseModel):
  """남자/여자 일주 조합별 미리 준비된 궁합 태그"""

  class Meta:
    db_table = "prepared_compatibility_tags"
    verbose_name = "Prepared Compatibility Tag"
    verbose_name_plural = "Prepared Compatibility Tags"
    indexes = [
      # 남자 일주, 여자 일주로 조회
      models.Index(
        fields=["male_d_stem", "male_d_branch", "female_d_stem", "female_d_branch"],
        name="idx_male_female_ilju",
      ),
      # 여자 일주로만 조회 (역방향 조회 등)
      models.Index(
        fields=["female_d_stem", "female_d_branch"],
        name="idx_female_ilju",
      ),
    ]
    unique_together = [["male_d_stem", "male_d_branch", "female_d_stem", "female_d_branch"]]

  # 남자 일주
  male_d_stem = models.CharField(
    max_length=1,
    choices=StemChoice.get_choices(),
    verbose_name="남자 일간",
  )
  male_d_branch = models.CharField(
    max_length=1,
    choices=BranchChoice.get_choices(),
    verbose_name="남자 일지",
  )

  # 여자 일주
  female_d_stem = models.CharField(
    max_length=1,
    choices=StemChoice.get_choices(),
    verbose_name="여자 일간",
  )
  female_d_branch = models.CharField(
    max_length=1,
    choices=BranchChoice.get_choices(),
    verbose_name="여자 일지",
  )

  compatibility_tags = models.ManyToManyField(
    "matchmakings.CompatibilityTag",
    related_name="prepared_compatibility_tags",
    verbose_name="궁합 태그",
    blank=True,
  )

  def __str__(self):
    return f"남자:{self.male_d_stem}{self.male_d_branch} 여자:{self.female_d_stem}{self.female_d_branch}"
