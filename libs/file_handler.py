import os
from datetime import datetime

def is_duplicate_url(rules_dir: str, url: str) -> bool:
    """
    지정된 디렉터리 내의 모든 .txt 파일에서 URL 중복을 검사합니다.
    AdGuard 기본 형식인 '||url^'을 기준으로 검색합니다.

    Args:
        rules_dir (str): 규칙 파일들이 있는 루트 디렉터리 경로.
        url (str): 중복 검사할 URL.

    Returns:
        bool: 중복된 URL이 있으면 True, 없으면 False를 반환합니다.
    """
    if not os.path.exists(rules_dir):
        return False # 검사할 디렉터리가 없으면 중복이 없는 것으로 간주

    search_pattern = f"||{url}^"

    for root, _, files in os.walk(rules_dir):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if search_pattern in line:
                                return True
                except (IOError, UnicodeDecodeError) as e:
                    print(f"경고: '{file_path}' 파일을 읽는 중 오류 발생: {e}")
                    continue # 파일 읽기 오류 시 해당 파일은 건너뜀
    return False

def format_adguard_url(url: str, is_important: bool) -> str:
    """
    주어진 URL을 AdGuard 규칙 형식으로 변환합니다.

    Args:
        url (str): 변환할 원본 URL.
        is_important (bool): important 태그 추가 여부.

    Returns:
        str: AdGuard 규칙 형식으로 변환된 문자열.
    """
    base_rule = f"||{url}^"
    if is_important:
        return f"{base_rule}$important"
    return base_rule

def _get_current_version(file_path: str) -> str | None:
    """기존 규칙 파일에서 버전 문자열을 추출합니다."""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith("! Version:"):
                    # "! Version: 1.0.0" -> " 1.0.0" -> "1.0.0"
                    return line.split(":", 1)[1].strip()
    except IOError:
        return None # 파일 읽기 실패
    return None # 버전 라인을 찾지 못함

def _calculate_next_version(current_version: str | None) -> str:
    """
    주어진 현재 버전을 기반으로 다음 버전을 계산합니다.
    - 업데이트 시: patch 버전 +1
    - patch 버전이 10이 되면: minor 버전 +1, patch는 0으로 초기화
    """
    if current_version is None:
        return "1.0.0" # 새 파일의 시작 버전
    
    try:
        parts = current_version.split('.')
        if len(parts) != 3:
            print(f"경고: 버전 형식이 올바르지 않습니다 ('{current_version}'). 버전 '1.0.0'부터 다시 시작합니다.")
            return "1.0.0"
            
        major, minor, patch = map(int, parts)
        
        patch += 1
        if patch >= 10:
            patch = 0
            minor += 1
        
        return f"{major}.{minor}.{patch}"
    except (ValueError, IndexError):
        print(f"경고: 버전 파싱에 실패했습니다 ('{current_version}'). 버전 '1.0.0'부터 다시 시작합니다.")
        return "1.0.0"

def _generate_metadata_header(category: str, version: str) -> list[str]:
    """규칙 파일의 메타데이터 헤더를 생성합니다."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    title = f"{category.capitalize()} DNS Rule"
    
    header = [
        f"! Title: {title}",
        f"! Version: {version}",
        f"! Date: {date_str}",
        "! Homepage: https://github.com/op6161/adblock_dns_rule",
        "" # 메타데이터와 규칙 목록 사이의 공백 라인
    ]
    return header

def add_url_to_file(file_path: str, new_rule: str, category: str):
    """
    지정된 파일에 URL을 추가하고 메타데이터 헤더를 업데이트합니다.
    파일이 존재하지 않으면 새로 생성하고, 존재하면 내용을 읽어와 업데이트 후 덮어씁니다.

    Args:
        file_path (str): 내용을 추가할 파일의 전체 경로.
        new_rule (str): 추가할 AdGuard 형식의 규칙.
        category (str): 파일 제목 생성을 위한 카테고리 이름.
    
    Raises:
        IOError: 파일 쓰기 권한이 없는 등 파일 관련 문제가 발생할 경우.
    """
    # 1. 파일이 위치할 디렉터리가 없으면 생성합니다.
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print(f"생성: '{dir_name}' 디렉터리.")

    # 2. 다음 버전을 계산합니다.
    current_version = _get_current_version(file_path)
    next_version = _calculate_next_version(current_version)

    # 3. 기존 파일이 있다면, 헤더를 제외한 규칙들만 읽어옵니다.
    existing_rules = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # '!'로 시작하지 않는 비어있지 않은 라인만 규칙으로 간주
                existing_rules = [line.strip() for line in lines if not line.strip().startswith('!') and line.strip()]
        except IOError as e:
            print(f"경고: '{file_path}' 파일을 읽는 중 오류 발생: {e}")

    # 4. 새로운 규칙을 목록에 추가합니다 (중복 방지).
    if new_rule not in existing_rules:
        existing_rules.append(new_rule)
    
    # 5. 규칙 목록을 알파벳순으로 정렬하여 일관성을 유지합니다.
    existing_rules.sort()

    # 6. 새로운 메타데이터 헤더를 생성합니다.
    new_header_lines = _generate_metadata_header(category, next_version)
    
    # 7. 새로운 헤더와 정렬된 규칙 목록을 합쳐 파일에 쓸 최종 내용을 만듭니다.
    final_content_lines = new_header_lines + existing_rules

    # 8. 파일에 전체 내용을 덮어씁니다.
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_content_lines) + '\n')

# ===== 아래 함수를 파일 끝에 새로 추가해주세요 =====
def update_copied_file(file_path: str, rules: list[str], category: str):
    """
    외부에서 가져온 규칙 목록으로 파일을 덮어쓰고, 메타데이터를 추가합니다.
    버전은 날짜 기반으로 생성됩니다.

    Args:
        file_path (str): 덮어쓸 파일의 전체 경로.
        rules (list[str]): 외부에서 가져온 규칙 문자열의 리스트.
        category (str): 파일 제목 생성을 위한 카테고리 이름.
    """
    # 1. 디렉터리가 없으면 생성
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # 2. 날짜 기반으로 버전 생성 (예: 20231027.1130)
    version = datetime.now().strftime("%Y%m%d.%H%M")
    
    # 3. 메타데이터 헤더 생성
    header_lines = _generate_metadata_header(category, version)
    
    # 4. 규칙 목록 정렬
    rules.sort()
    
    # 5. 최종 내용 조합
    final_content_lines = header_lines + rules
    
    # 6. 파일에 덮어쓰기
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_content_lines) + '\n')

