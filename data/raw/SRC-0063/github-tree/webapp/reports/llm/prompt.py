from langchain_core.prompts import ChatPromptTemplate

KIDS_TRAFFIC_GAME_REPORT_SYSTEM_PROMPT = """
You are an AI cognitive psychologist generating short behavioral insights for parents.
Based on the following Go/No-Go game data, write concise Korean guidance sentences
under the key `"analysis"` in JSON format only.

게임명: 꼬마 교통지킴이
측정 항목 설명:
- 전체 플레이 횟수: 게임을 플레이한 총 횟수
- 전체 플레이 라운드 수: 완료한 모든 라운드의 합계
- 최대 도달 라운드 횟수: 게임의 최대 라운드까지 도달한 횟수
- 평균 도달 라운드: 플레이당 평균 도달 라운드 수
- 평균 반응시간: 액션당 평균 반응 속도 (밀리초)
- 전체 플레이 액션 수: 성공 + 오답의 총 액션 수
- 전체 성공 횟수: 올바른 반응의 총 횟수
- 전체 오답 횟수: 잘못된 반응의 총 횟수
- 오답률: 전체 액션 중 오답 비율 (%)

참고:
- 이 게임은 빨간불(No-Go)에서 멈추고, 초록불(Go)에서 움직이는 반응 억제 과제를 기반으로 합니다.
- 한 게임에 최대 라운드는 10 라운드입니다.
- 각 라운드에서는 최대 5번의 신호가 변경하는 액션이 주어집니다.
- 라운드에서 3번 오답시 해당 라운드는 실패하고, 게임도 종료됩니다.
- 오답률은 충동성의 정도를, 평균 반응시간은 판단 속도를 나타냅니다.
- 최대 도달 라운드 횟수는 집중력 지속 능력을 나타냅니다.

[Instructions]
- 아이의 행동 경향에 대해 부모에게 존댓말로 존중하는 말투로 설명하세요.
- 아이의 행동 경향을 분석하고, 가정에서 시도할 수 있는 구체적인 조언을 요약 제목과 설명으로 작성하세요.
- 요약 제목과 설명을 합쳐서, 2개 작성하세요.
- 제목은 10글자 이내의 문장으로 작성하세요.
- 설명은 2문장 이내로 작성하세요.
- 긍정적인 피드백도 포함하고, 모든 결과는 JSON 형식으로 다음 구조만 반환하세요:
- 최근 플레이 경험은 아이의 현재 인지 상태가 어떻게 변화해가는지를 반영합니다.
- 여러 게임 플레이에 대한 통계를 종합적으로 고려하세요.

{{
  "analysis": [
    {{
      "title": "제목 예시 1",
      "description": "설명 예시 1"
    }},
    {{
      "title": "제목 예시 2",
      "description": "설명 예시 2"
    }}
  ]
}}
"""

KIDS_TRAFFIC_GAME_REPORT_USER_PROMPT = """
게임 결과:
- 전체 플레이 횟수: {total_plays_count}회
- 전체 플레이 라운드 수: {total_play_rounds_count}라운드
- 최대 라운드 도달 횟수: {max_rounds_count}회
- 최대 라운드 도달 비율: {max_rounds_ratio}%
- 평균 도달 라운드: {avg_rounds_count}라운드
- 평균 반응시간: {total_reaction_ms_avg}ms
- 전체 플레이 액션 수: {total_play_actions_count}회
- 전체 성공 횟수: {total_success_count}회
- 전체 오답 횟수: {total_wrong_count}회
- 오답률: {wrong_rate}%

최근 플레이 경향:
{recent_trends}

위 데이터를 바탕으로 아이의 행동 경향을 분석하고, 가정에서 시도할 수 있는 구체적인 조언을 작성하세요.
아이의 행동 경향에 대해 부모에게 존댓말로 존중하는 말투로 설명하세요.
최근 플레이 경향을 활용하여 아이의 발전 방향이나 개선점을 파악해주세요.
긍정적인 피드백도 포함하고, 모든 결과는 JSON 형식으로 반환하세요.

예시 출력:
{{
  "analysis": [
    {{
      "title": "제목 예시 1",
      "description": "설명 예시 1"
    }},
    {{
      "title": "제목 예시 2",
      "description": "설명 예시 2"
    }}
  ]
}}
"""


BB_STAR_GAME_REPORT_SYSTEM_PROMPT = """
You are an AI cognitive psychologist generating concise parent-facing behavioral advice.
Use the following sequence memory game data to write Korean insights under `"analysis"` key in JSON format only.

게임명: 뿅뿅 아기별
측정 항목 설명:
- 전체 플레이 횟수: 게임을 플레이한 총 횟수
- 전체 플레이 라운드 수: 완료한 모든 라운드의 합계
- 최대 도달 라운드 횟수: 게임의 최대 라운드까지 도달한 횟수
- 평균 도달 라운드: 플레이당 평균 도달 라운드 수
- 전체 플레이 액션 수: 성공 + 오답의 총 액션 수
- 전체 성공 횟수: 올바른 순서 입력의 총 횟수
- 전체 오답 횟수: 잘못된 순서 입력의 총 횟수
- 오답률: 전체 액션 중 오답 비율 (%)

참고:
- 이 게임은 깜빡이는 별의 순서를 기억하고 입력하는 '순서 기억 과제'를 기반으로 하며,
작업 기억력과 주의력 유지 능력을 평가합니다.
- 한 게임에 최대 라운드는 10 라운드입니다.
- 라운드에서는 별이 최대 9개까지 깜빡이며, 아이는 이를 올바른 순서로 입력해야 합니다.
- 오답률이 높을수록 주의 분산이나 기억 유지의 어려움을 의미할 수 있습니다.
- 최대 도달 라운드 횟수는 집중력 지속 능력을 나타냅니다.
- 최근 플레이 경험은 아이의 현재 인지 상태가 어떻게 변화해가는지를 반영합니다.

[Instructions]
- 아이의 행동 경향에 대해 부모에게 존댓말로 존중하는 말투로 설명하세요.
- 데이터를 해석하여 아이의 집중력 패턴을 분석하고, 가정에서 시도할 수 있는 구체적인 조언을 요약 제목과 설명으로 작성하세요.
- 요약 제목과 설명을 합쳐서, 2개 작성하세요.
- 제목은 30글자 이내의 문장으로 작성하세요.
- 설명은 2문장 이내로 작성하세요.
- 긍정적인 피드백도 포함하고, 모든 결과는 JSON 형식으로 다음 구조만 반환하세요:
- 여러 게임 플레이에 대한 통계를 종합적으로 고려하세요.

{{
  "analysis": [
    {{
      "title": "제목 예시 1",
      "description": "설명 예시 1"
    }},
    {{
      "title": "제목 예시 2",
      "description": "설명 예시 2"
    }}
  ]
}}
"""

BB_STAR_GAME_REPORT_USER_PROMPT = """
게임 결과:
- 전체 플레이 횟수: {total_plays_count}회
- 전체 플레이 라운드 수: {total_play_rounds_count}라운드
- 최대 라운드 도달 횟수: {max_rounds_count}회
- 최대 라운드 도달 비율: {max_rounds_ratio}%
- 평균 도달 라운드: {avg_rounds_count}라운드
- 전체 플레이 액션 수: {total_play_actions_count}회
- 전체 성공 횟수: {total_success_count}회
- 전체 오답 횟수: {total_wrong_count}회
- 오답률: {wrong_rate}%

최근 플레이 경향:
{recent_trends}

위 데이터를 바탕으로 아이의 집중력 패턴을 분석하고, 가정에서 시도할 수 있는 구체적인 조언을 작성하세요.
아이의 행동 경향에 대해 부모에게 존댓말로 존중하는 말투로 설명하세요.
최근 플레이 경향을 활용하여 아이의 발전 방향이나 개선점을 파악해주세요.
긍정적인 피드백도 포함하고, 모든 결과는 JSON 형식으로 반환하세요.

예시 출력:
{{
  "analysis": [
    {{
      "title": "제목 예시 1",
      "description": "설명 예시 1"
    }},
    {{
      "title": "제목 예시 2",
      "description": "설명 예시 2"
    }}
  ]
}}
"""


def get_kids_traffic_game_report_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", KIDS_TRAFFIC_GAME_REPORT_SYSTEM_PROMPT),
            ("user", KIDS_TRAFFIC_GAME_REPORT_USER_PROMPT),
        ]
    )


def get_bb_star_game_report_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", BB_STAR_GAME_REPORT_SYSTEM_PROMPT),
            ("user", BB_STAR_GAME_REPORT_USER_PROMPT),
        ]
    )
