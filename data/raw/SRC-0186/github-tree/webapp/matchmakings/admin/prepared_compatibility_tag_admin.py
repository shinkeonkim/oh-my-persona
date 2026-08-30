import json

from django.contrib import admin

from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from common.utils.logger import get_logger
from matchmakings.models import CompatibilityTag, PreparedCompatibilityTag

logger = get_logger(__name__)


class PreparedCompatibilityTagResource(resources.ModelResource):
  """PreparedCompatibilityTag 모델을 위한 import/export 리소스"""

  # ManyToMany 필드를 명시적으로 선언 (readonly=True로 bulk_update에서 제외)
  compatibility_tags = fields.Field(column_name="compatibility_tags", attribute="compatibility_tags", readonly=True)

  class Meta:
    model = PreparedCompatibilityTag
    fields = ("male_d_stem", "male_d_branch", "female_d_stem", "female_d_branch", "compatibility_tags")
    export_order = ("male_d_stem", "male_d_branch", "female_d_stem", "female_d_branch", "compatibility_tags")
    import_id_fields = ("male_d_stem", "male_d_branch", "female_d_stem", "female_d_branch")
    skip_unchanged = True
    report_skipped = False
    use_bulk = True
    batch_size = 500

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # 태그 캐시: {tag_name: CompatibilityTag object}
    self._tag_cache = {}
    # M2M 관계 임시 저장: {instance_id: [tag1, tag2, ...]}
    self._m2m_data = {}

  def dehydrate_compatibility_tags(self, obj):
    """Export 시 태그들을 JSON 배열로 변환"""
    return json.dumps([tag.name for tag in obj.compatibility_tags.all()], ensure_ascii=False)

  def skip_row(self, instance, original, row, import_validation_errors=None):  # noqa: ARG002
    """
    ManyToMany 관계는 나중에 처리하므로 skip_unchanged 로직을 수정
    """
    # 기본 필드만 비교 (male_d_stem, male_d_branch, female_d_stem, female_d_branch)
    return False

  def get_bulk_update_fields(self):
    """
    bulk_update에 사용할 필드 목록 반환
    ManyToMany 필드는 bulk_update에서 제외
    """
    # concrete fields만 반환 (ManyToMany 제외)
    return ["male_d_stem", "male_d_branch", "female_d_stem", "female_d_branch"]

  def before_import(self, dataset, **kwargs):
    """Import 시작 전 모든 태그를 미리 로드하여 캐싱"""
    # 데이터셋에서 모든 태그 이름 추출
    all_tag_names = set()
    for row in dataset.dict:
      tags_data = row.get("compatibility_tags", "")

      try:
        if tags_data:
          tag_names = json.loads(tags_data)
          all_tag_names.update(tag.strip() for tag in tag_names if tag.strip())
      except (json.JSONDecodeError, ValueError):
        pass

    # 기존 태그들을 한 번에 조회하여 캐시
    existing_tags = CompatibilityTag.objects.filter(name__in=all_tag_names)
    self._tag_cache = {tag.name: tag for tag in existing_tags}

    # 존재하지 않는 태그들을 bulk_create
    existing_tag_names = set(self._tag_cache.keys())
    new_tag_names = all_tag_names - existing_tag_names

    if new_tag_names:
      new_tags = [CompatibilityTag(name=name) for name in new_tag_names]
      CompatibilityTag.objects.bulk_create(new_tags, ignore_conflicts=True)

      # bulk_create 후 다시 조회하여 캐시에 추가 (ID를 얻기 위함)
      newly_created = CompatibilityTag.objects.filter(name__in=new_tag_names)
      for tag in newly_created:
        self._tag_cache[tag.name] = tag

    logger.info(
      "PreparedCompatibilityTag import: 태그 캐시 완료",
      total_tags=len(self._tag_cache),
      new_tags_created=len(new_tag_names),
    )

  def before_import_row(self, row, **kwargs):
    """Import 전에 row 데이터 전처리"""
    # compatibility_tags를 임시로 저장
    self._current_tags_data = row.get("compatibility_tags", "")

  def after_save_instance(self, instance, row, **kwargs):
    """인스턴스 저장 후 ManyToMany 관계 데이터 수집"""
    tags = []

    # 태그 데이터 처리
    tags_data = getattr(self, "_current_tags_data", "")
    if tags_data:
      try:
        tag_names = json.loads(tags_data)
        for tag_name in tag_names:
          tag_name = tag_name.strip()
          if tag_name and tag_name in self._tag_cache:
            tags.append(self._tag_cache[tag_name])
      except (json.JSONDecodeError, ValueError) as e:
        logger.warning(
          "태그 파싱 오류",
          instance_id=instance.id,
          error=str(e),
          data_preview=tags_data[:100],
        )

    # M2M 데이터를 나중에 처리하기 위해 저장
    if tags:
      self._m2m_data[instance.id] = tags

  def after_import(self, dataset, result, **kwargs):
    """Import 완료 후 모든 ManyToMany 관계를 bulk로 처리"""
    if not self._m2m_data:
      return

    logger.info("PreparedCompatibilityTag import: M2M 관계 bulk 처리 시작", count=len(self._m2m_data))

    # 모든 인스턴스를 한 번에 조회
    instance_ids = list(self._m2m_data.keys())
    instances = {
      obj.id: obj
      for obj in PreparedCompatibilityTag.objects.filter(id__in=instance_ids).prefetch_related("compatibility_tags")
    }

    # M2M 관계 설정
    for instance_id, tags in self._m2m_data.items():
      if instance_id in instances:
        instance = instances[instance_id]
        instance.compatibility_tags.set(tags)

    logger.info("PreparedCompatibilityTag import: M2M 관계 bulk 처리 완료")

    # 메모리 정리
    self._m2m_data.clear()
    self._tag_cache.clear()


@admin.register(PreparedCompatibilityTag)
class PreparedCompatibilityTagAdmin(ModelAdmin, ImportExportModelAdmin):
  """Prepared Compatibility Tag 관리 어드민"""

  # Import/Export 설정
  resource_class = PreparedCompatibilityTagResource
  import_form_class = ImportForm
  export_form_class = ExportForm

  list_display = (
    "id",
    "male_ilju",
    "female_ilju",
    "display_compatibility_tags",
    "created_at",
  )
  list_filter = (
    "male_d_stem",
    "male_d_branch",
    "female_d_stem",
    "female_d_branch",
  )
  search_fields = ("compatibility_tags__name", )
  filter_horizontal = ("compatibility_tags", )
  ordering = ("male_d_stem", "male_d_branch", "female_d_stem", "female_d_branch")

  fieldsets = (
    (
      "남자 일주",
      {
        "fields": (
          "male_d_stem",
          "male_d_branch",
        ),
      },
    ),
    (
      "여자 일주",
      {
        "fields": (
          "female_d_stem",
          "female_d_branch",
        ),
      },
    ),
    (
      "궁합 태그",
      {
        "fields": ("compatibility_tags", ),
      },
    ),
  )

  list_per_page = 50
  list_filter_submit = True
  list_filter_sheet = False

  def male_ilju(self, obj):
    """남자 일주"""
    return f"{obj.male_d_stem}{obj.male_d_branch}"

  male_ilju.short_description = "남자 일주"

  def female_ilju(self, obj):
    """여자 일주"""
    return f"{obj.female_d_stem}{obj.female_d_branch}"

  female_ilju.short_description = "여자 일주"

  def display_compatibility_tags(self, obj):
    """궁합 태그 목록 표시"""
    tags = obj.compatibility_tags.all()[:5]
    tag_str = ", ".join([tag.name for tag in tags])
    if obj.compatibility_tags.count() > 5:
      tag_str += f" (+{obj.compatibility_tags.count() - 5}개)"
    return tag_str

  display_compatibility_tags.short_description = "궁합 태그"

  def get_queryset(self, request):
    queryset = super().get_queryset(request)
    return queryset.prefetch_related("compatibility_tags")
