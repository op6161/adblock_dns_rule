import json
import os
import sys
from datetime import datetime
import requests # pip install requests 필요

# 프로젝트 루트 경로 설정
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from rule.libs import file_handler
from rule.libs import git_handler

CONFIG_FILE_PATH = os.path.join("rule", "copy_sources.json")
RULES_BASE_DIR = os.path.join("rule", "rules")

def fetch_content_from_url(url: str) -> str | None:
    """주어진 URL에서 텍스트 콘텐츠를 가져옵니다."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status() # 200 OK가 아니면 예외 발생
        return response.text
    except requests.RequestException as e:
        print(f"오류: '{url}'에서 콘텐츠를 가져오는 데 실패했습니다: {e}")
        return None

def clean_external_rules(raw_content: str) -> list[str]:
    """가져온 원본 콘텐츠에서 주석, 빈 줄 등을 제거하고 규칙만 남깁니다."""
    cleaned_lines = []
    for line in raw_content.splitlines():
        stripped_line = line.strip()
        # 주석이 아니고, 비어있지 않은 라인만 추가
        if stripped_line and not stripped_line.startswith(('!', '#', '/')):
            cleaned_lines.append(stripped_line)
    return cleaned_lines

def main():
    """설정 파일을 읽어 외부 규칙 목록을 갱신하고 Git에 커밋합니다."""
    print("외부 규칙 목록 자동 갱신을 시작합니다...")
    
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            sources = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"오류: 설정 파일('{CONFIG_FILE_PATH}')을 읽을 수 없습니다: {e}")
        return

    updated_files = []
    for category, items in sources.items():
        for item in items:
            filename = item.get("filename")
            url = item.get("url")

            if not filename or not url:
                print(f"경고: '{category}' 카테고리의 항목에 filename 또는 url이 없습니다. 건너뜁니다.")
                continue

            print(f"\n[{category}/{filename}] 갱신 중...")
            print(f"-> 소스 URL: {url}")

            # 1. URL에서 콘텐츠 가져오기
            raw_content = fetch_content_from_url(url)
            if raw_content is None:
                continue # 실패 시 다음 파일로

            # 2. 가져온 콘텐츠에서 순수 규칙만 필터링
            rules = clean_external_rules(raw_content)
            if not rules:
                print("-> 가져온 콘텐츠에 유효한 규칙이 없어 건너뜁니다.")
                continue
            
            # 3. 파일에 갱신된 내용 쓰기
            target_path = os.path.join(RULES_BASE_DIR, category, filename)
            try:
                # file_handler에 새 함수를 만들어 사용할 예정
                file_handler.update_copied_file(target_path, rules, category)
                print(f"-> 성공: '{target_path}' 파일이 {len(rules)}개의 규칙으로 갱신되었습니다.")
                updated_files.append(target_path)
            except IOError as e:
                print(f"-> 오류: '{target_path}' 파일 쓰기에 실패했습니다: {e}")

    # 4. 변경된 파일이 있으면 Git 커밋 및 푸시
    if updated_files:
        print("\n모든 파일 갱신 완료. Git 작업을 시작합니다...")
        try:
            commit_message = f"Chore: Update {len(updated_files)} external rule list(s)"
            git_handler.git_add(updated_files) # 여러 파일을 한번에 add
            git_handler.git_commit(commit_message)
            git_handler.git_push()
            print("Git 커밋 및 푸시 완료! ✅")
        except Exception as e:
            print(f"Git 작업 중 오류가 발생했습니다: {e}")
    else:
        print("\n갱신된 파일이 없습니다. 작업을 종료합니다.")


if __name__ == "__main__":
    main()
