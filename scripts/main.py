import argparse
import os
import sys

# 프로젝트 루트 경로를 시스템 경로에 추가하여 rule.libs 모듈을 임포트할 수 있도록 합니다.
# 이 스크립트는 프로젝트 루트 디렉터리에서 실행되어야 합니다. (예: python rule/scripts/main.py ...)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from rule.libs import file_handler
from rule.libs import git_handler
from rule.libs import category_handler

def main():
    """
    메인 실행 함수입니다.
    명령줄 인수를 파싱하여 URL 중복 검사, 파일 추가, Git 커밋 및 푸시를 수행합니다.
    """
    # 1. 명령줄 인수 파서 설정
    parser = argparse.ArgumentParser(description="URL을 AdGuard 규칙 파일에 추가하고 Git에 커밋합니다.")
    parser.add_argument("url", type=str, help="추가할 차단 대상 URL (예: google.com)")
    parser.add_argument("category", type=str, help="규칙 파일의 카테고리 (예: naver)")
    parser.add_argument("--important", action="store_true", help="URL에 '$important' 태그를 추가합니다.")
    parser.add_argument("--risk", action="store_true", help="URL을 '_risk.txt' 파일에 추가합니다.")
    
    args = parser.parse_args()

    # 2. 카테고리 이름 표준화
    standard_category = category_handler.normalize_category(args.category)
    print(f"입력된 카테고리 '{args.category}' -> 표준 카테고리 '{standard_category}'(으)로 변환되었습니다.")

    # 3. 기본 경로 설정
    rules_base_dir = os.path.join("rule", "rules")

    # 4. URL 중복 검사
    print(f"'{args.url}'이(가) 기존 규칙에 있는지 확인합니다...")
    if file_handler.is_duplicate_url(rules_base_dir, args.url):
        print(f"경고: '{args.url}'은(는) 이미 다른 규칙 파일에 존재합니다. 작업을 건너뜁니다.")
        return 

    print("중복된 URL이 없습니다. 다음 단계를 진행합니다.")

    # 5. 파일 경로 및 내용 생성
    file_suffix = "_risk.txt" if args.risk else ".txt"
    file_name = f"{standard_category}{file_suffix}"
    target_dir = os.path.join(rules_base_dir, standard_category)
    target_file_path = os.path.join(target_dir, file_name)
    
    formatted_url = file_handler.format_adguard_url(args.url, args.important)

    # 6. 파일에 URL 추가 (변경된 함수 호출)
    try:
        # file_handler.add_url_to_file에 standard_category 인자 추가
        file_handler.add_url_to_file(target_file_path, formatted_url, standard_category)
        print(f"성공: '{target_file_path}' 파일에 규칙을 추가하고 메타데이터를 업데이트했습니다.")
    except IOError as e:
        print(f"오류: 파일에 쓰는 중 문제가 발생했습니다 - {e}")
        return

    # 7. Git 작업 수행
    try:
        print("Git 작업을 시작합니다...")
        commit_message = f"Update: {standard_category} rules with {args.url}"
        
        git_handler.git_add(target_file_path)
        print(f"Git Staged: {target_file_path}")

        git_handler.git_commit(commit_message)
        print(f"Git Committed: \"{commit_message}\"")

        git_handler.git_push()
        print("Git Push: 원격 저장소로 푸시 완료.")
        
        print("\n모든 작업이 성공적으로 완료되었습니다. ✅")

    except Exception as e:
        print(f"\nGit 작업 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()

