# 카테고리 별칭을 표준 이름으로 매핑하는 딕셔너리입니다.
# 여기에 계속해서 별칭을 추가하여 관리할 수 있습니다.
# 키(key)가 표준 이름이 되며, 값(value)은 해당 표준 이름으로 인식될 별칭들의 리스트입니다.
CATEGORY_ALIASES = {
    # 표준이름: [별칭1, 별칭2, ...]
    'google': ['구글', 'rnrmf', 'google.com'],
    'naver': ['네이버', 'spdlqj', 'naver.com'],
    'daum': ['다음', 'ekdna', 'daum.net'],
    'spam': ['스팸'],
    'security': ['보안'],
    'malware': ['멀웨어', '악성코드'],
}

def normalize_category(alias: str) -> str:
    """
    주어진 카테고리 별칭(alias)을 표준 카테고리 이름으로 변환합니다.

    Args:
        alias (str): 사용자가 입력한 카테고리 이름.

    Returns:
        str: 매핑된 표준 카테고리 이름. 매핑되는 이름이 없으면 입력값을 그대로 반환.
    """
    # 입력값을 소문자로 변환하여 일관성을 유지합니다.
    alias_lower = alias.lower()
    
    # 1. 입력값 자체가 표준 이름(딕셔너리의 키) 중 하나인지 확인합니다.
    if alias_lower in CATEGORY_ALIASES:
        return alias_lower
        
    # 2. 딕셔너리를 순회하며 별칭 리스트에 입력값이 포함되어 있는지 확인합니다.
    for standard_name, aliases in CATEGORY_ALIASES.items():
        # 별칭 리스트의 모든 항목을 소문자로 변환하여 비교합니다.
        if alias_lower in [a.lower() for a in aliases]:
            return standard_name # 일치하는 표준 이름을 찾으면 반환
            
    # 3. 매핑되는 항목이 없으면, 원래 입력값을 그대로 반환합니다.
    return alias