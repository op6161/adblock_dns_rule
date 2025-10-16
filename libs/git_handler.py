import subprocess

def git_add(file_paths: str | list[str]):
    """
    지정된 파일(들)을 Git 스테이징 영역에 추가합니다.
    
    Args:
        file_paths (str | list[str]): 스테이징할 파일의 경로 또는 경로 리스트.
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths] # 단일 파일 경로도 리스트로 변환
    
    command = ["git", "add"] + file_paths
    subprocess.run(command, check=True, capture_output=True, text=True)

def git_commit(message: str):
    """
    스테이징된 변경 사항을 커밋합니다.

    Args:
        message (str): 커밋 메시지.
    """
    command = ["git", "commit", "-m", message]
    subprocess.run(command, check=True, capture_output=True, text=True)

def git_push(remote: str = "origin", branch: str = "main"):
    """
    로컬 브랜치의 변경 사항을 원격 저장소로 푸시합니다.

    Args:
        remote (str): 원격 저장소 이름 (기본값: "origin").
        branch (str): 푸시할 브랜치 이름 (기본값: "main").
    """
    command = ["git", "push", remote, branch]
    subprocess.run(command, check=True, capture_output=True, text=True)

