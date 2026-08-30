"""중개인 종합의견 생성을 위한 프롬프트"""


class OverallOpinionPrompt:
  """중개인의 종합의견 생성을 위한 프롬프트 모음"""

  SYSTEM_PROMPT = """당신은 사주 기반 소개팅 서비스의 전문 중개인입니다.
두 사람의 사주 정보와 프로필을 분석하여, 각 성별에게 맞춤형 종합의견을 제시합니다.
의견은 따뜻하고 격려적이며, 사주의 깊이있는 해석을 포함해야 합니다."""

  @staticmethod
  def get_male_opinion_prompt(user_data: dict, referral_user_data: dict) -> str:
    """
        남자에게 보여줄 종합의견 생성 프롬프트

        Args:
            user_data: 사용자(남자)의 정보 (프로필, 사주 차트 등)
            referral_user_data: 추천된 사용자(여자)의 정보

        Returns:
            프롬프트 문자열
        """
    # 데이터를 문자열로 변환
    male_saju = str(user_data.get('saju_chart', {}))
    male_profile = str(user_data.get('profile', {}))
    female_saju = str(referral_user_data.get('saju_chart', {}))
    female_profile = str(referral_user_data.get('profile', {}))

    prompt = f"""다음은 두 사람의 정보입니다:

[남자 (본인)]
- 사주: {male_saju}
- 프로필: {male_profile}

[여자 (추천 상대)]
- 사주: {female_saju}
- 프로필: {female_profile}

위 정보를 바탕으로 남자에게 전달할 중개인의 종합의견을 작성해주세요.

작성 시 고려사항:
1. 두 사람의 사주 궁합을 분석하고, 어떤 점이 잘 맞는지 설명
2. 여자의 매력적인 특징과 강점 강조
3. 이 인연이 남자에게 어떤 긍정적 영향을 줄 수 있는지
4. 따뜻하고 격려적인 톤으로 작성
5. 약 200-300자 분량
6. 한국어로 작성
7. 상대를 존중하는 표현 사용

출력 형식 (JSON):
{{
  "content": "생성된 종합의견"
}}
"""

    return prompt

  @staticmethod
  def get_female_opinion_prompt(user_data: dict, referral_user_data: dict) -> str:
    """
        여자에게 보여줄 종합의견 생성 프롬프트

        Args:
            user_data: 사용자(여자)의 정보 (프로필, 사주 차트 등)
            referral_user_data: 추천된 사용자(남자)의 정보

        Returns:
            프롬프트 문자열
        """
    # 데이터를 문자열로 변환
    female_saju = str(user_data.get('saju_chart', {}))
    female_profile = str(user_data.get('profile', {}))
    male_saju = str(referral_user_data.get('saju_chart', {}))
    male_profile = str(referral_user_data.get('profile', {}))

    prompt = f"""다음은 두 사람의 정보입니다:

[여자 (본인)]
- 사주: {female_saju}
- 프로필: {female_profile}

[남자 (추천 상대)]
- 사주: {male_saju}
- 프로필: {male_profile}

위 정보를 바탕으로 여자에게 전달할 중개인의 종합의견을 작성해주세요.

작성 시 고려사항:
1. 두 사람의 사주 궁합을 분석하고, 어떤 점이 잘 맞는지 설명
2. 남자의 매력적인 특징과 강점 강조
3. 이 인연이 여자에게 어떤 긍정적 영향을 줄 수 있는지
4. 따뜻하고 격려적인 톤으로 작성
5. 약 200-300자 분량
6. 한국어로 작성
7. 상대를 존중하는 표현 사용

출력 형식 (JSON):
{{
  "content": "생성된 종합의견"
}}
"""

    return prompt
