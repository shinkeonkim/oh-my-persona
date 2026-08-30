"""
한글의 경우 초성, 중성, 종성을 모두 분리한다.
이외의 문자는 그대로 분리한 채로 반환한다.
"""


class TextSplitter:
    first = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    second = (
        ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ"] +
        ["ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
    )
    third = (
        ["_", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ"] +
        [ "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ"] +
        ["ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    )

    def __init__(self, text):
        self.text = text

    def split(self):
        result = []
        for text in self.text:
            if ord("가") <= ord(text) <= ord("힣"):
                result += self._split_korean(text)
            else:
                result.append(text)
        return result

    def _split_korean(self, char):
        char_code = ord(char) - ord("가")
        char1 = char_code // 588
        char2 = (char_code - (588 * char1)) // 28
        char3 = char_code - (588 * char1) - 28 * char2

        if char3 == 0:
            return [self.first[char1], self.second[char2]]

        return [self.first[char1], self.second[char2], self.third[char3]]
