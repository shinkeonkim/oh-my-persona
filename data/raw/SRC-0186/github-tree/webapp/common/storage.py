"""
Custom storage classes for import_export
"""

import os
from uuid import uuid4

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from import_export.tmp_storages import BaseStorage


class MediaStorage(BaseStorage):
  """
  Django의 default storage를 사용하는 임시 스토리지

  Production 환경에서 여러 컨테이너가 동일한 파일에 접근할 수 있도록
  S3 등의 공유 스토리지를 활용합니다.

  - Preview와 Import 단계가 서로 다른 컨테이너에서 실행되어도 문제없음
  - settings.STORAGES 또는 DEFAULT_FILE_STORAGE 설정에 따라 자동으로 적용됨
  """

  def __init__(self, **kwargs):
    """
    BaseStorage 인터페이스에 맞춘 초기화

    kwargs:
        name: 파일 이름 (선택)
        read_mode: 읽기 모드 (기본값: 'r')
        encoding: 인코딩 (선택)
    """
    super().__init__(**kwargs)
    self.MEDIA_FOLDER = kwargs.get("MEDIA_FOLDER", "import_export_tmp")

  def get_full_path(self):
    """파일의 전체 경로 반환"""
    if self.MEDIA_FOLDER is not None:
      return os.path.join(self.MEDIA_FOLDER, self.name)
    return self.name

  def save(self, data):
    """
    파일 저장

    Args:
        data: 저장할 데이터 (bytes, str, file-like object)

    Returns:
        None (BaseStorage 인터페이스에 맞춤)
    """
    # 파일명이 없으면 고유한 이름 생성
    if not self.name:
      self.name = uuid4().hex

    # 데이터를 ContentFile로 변환
    if isinstance(data, str):
      content = ContentFile(data.encode("utf-8"))
    elif isinstance(data, bytes):
      content = ContentFile(data)
    elif hasattr(data, "read"):
      # 파일 객체인 경우
      if hasattr(data, "seek"):
        data.seek(0)
      file_content = data.read()
      if isinstance(file_content, str):
        content = ContentFile(file_content.encode("utf-8"))
      else:
        content = ContentFile(file_content)
    else:
      raise TypeError(f"Unsupported data type for save: {type(data)}")

    # default_storage를 통해 저장
    default_storage.save(self.get_full_path(), content)

  def read(self):
    """
    파일 읽기

    Returns:
        bytes or str: self.read_mode에 따라 반환 타입 결정
    """
    full_path = self.get_full_path()

    if not default_storage.exists(full_path):
      raise FileNotFoundError(f"Import file not found: {full_path}")

    # default_storage를 통해 파일 열기
    with default_storage.open(full_path, mode=self.read_mode) as f:
      return f.read()

  def remove(self):
    """파일 삭제"""
    full_path = self.get_full_path()
    if default_storage.exists(full_path):
      default_storage.delete(full_path)


# 기존 호환성을 위한 alias (필요시)
class CustomTempFolderStorage(MediaStorage):
  """CustomTempFolderStorage의 새로운 구현 (MediaStorage 사용)"""

  pass
