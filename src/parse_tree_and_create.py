#!/usr/bin/env python3
import os

# 트리 구조가 저장된 텍스트 파일
TREE_FILE_PATH = "project_tree.txt"

def find_marker_index(line: str) -> int:
    """
    한 줄에서 '├──' 또는 '└──'의 가장 왼쪽 인덱스를 찾는다.
    없으면 -1 리턴.
    """
    idx_arrow = line.find('├──')
    idx_corner = line.find('└──')
    if idx_arrow == -1 and idx_corner == -1:
        return -1
    elif idx_arrow == -1:
        return idx_corner
    elif idx_corner == -1:
        return idx_arrow
    else:
        return min(idx_arrow, idx_corner)

def get_depth(line: str) -> int:
    """
    트리 라인의 들여쓰기(│   ,    )를 세어서 depth 계산.
    - '├──' 또는 '└──' 위치를 찾고, 그 앞부분(prefix)에서
      4칸 단위('│   ' 또는 '    ')를 발견할 때마다 depth++
    """
    idx = find_marker_index(line)
    if idx == -1:
        # marker가 없으면 depth=0
        return 0
    prefix = line[:idx]

    depth = 0
    while True:
        prefix = prefix.lstrip('\t')  # 탭이 있다면 제거
        if prefix.startswith('│   '):
            depth += 1
            prefix = prefix[4:]
        elif prefix.startswith('    '):
            depth += 1
            prefix = prefix[4:]
        else:
            break
    return depth

def extract_raw_string(line: str) -> str:
    """
    해당 줄에서 실제 경로(폴더/파일) 부분만 잘라내어 반환.
    예) '│   ├── catkin_cartographer/catkin_cartographer/src'
     -> 'catkin_cartographer/catkin_cartographer/src'
    """
    s = line.strip()
    if s == '.':
        # 루트 표시
        return '.'
    idx = find_marker_index(s)
    if idx == -1:
        # marker가 없다면(장식줄 가능성)
        return s
    # '├──' / '└──'부터 3글자 뒤에서 시작
    # (예: '├── '는 4글자지만 여기서는 '──' 두 개를 replace로 처리)
    raw = s[idx+3:]
    # 혹시 남아있는 '─' 문자를 1개만 제거
    raw = raw.replace('─', '', 1).strip()
    return raw

def split_path_into_tokens(raw: str) -> list[str]:
    """
    슬래시('/')로 구분된 복합 경로를 토큰 리스트로 분할.
    예: 'catkin_cartographer/catkin_cartographer/src' -> ['catkin_cartographer','catkin_cartographer','src']
    예: '.' -> ['.']
    """
    if raw == '.':
        return ['.']
    parts = raw.split('/')
    # 공백이거나 빈 문자열은 제거
    parts = [p.strip() for p in parts if p.strip()]
    return parts

def is_file(token: str) -> bool:
    """
    토큰(폴더명/파일명)이 '파일'인지 판단하는 간단 규칙:
    1) '.'(마침표)가 들어 있으면 파일 (예: myfile.txt, test.sh 등)
    2) 나머지는 디렉토리
    3) 예외: 루트 '.' 는 디렉토리
    """
    if token == '.':
        return False  # 루트는 디렉토리로 처리
    if '.' in token:
        return True
    return False

def main():
    with open(TREE_FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 디렉토리 스택 (depth별로 어떤 폴더인지 추적)
    path_stack = ["."]
    os.makedirs(".", exist_ok=True)

    for line in lines:
        line = line.rstrip('\n')
        if not line.strip():
            # 빈 줄은 스킵
            continue

        # '├──', '└──'도 없고 '.'도 안 들어 있으면 => 장식 라인으로 간주 -> 스킵
        if find_marker_index(line) == -1 and '.' not in line:
            continue

        depth = get_depth(line)
        raw = extract_raw_string(line)
        if not raw:
            # 경로 부분이 비었으면 스킵
            continue

        # 스택 정리 (현재 depth보다 깊은 항목이 있으면 pop)
        while len(path_stack) > (depth + 1):
            path_stack.pop()

        # 슬래시가 있으면 여러 단계로 분할
        tokens = split_path_into_tokens(raw)
        if not tokens:
            continue

        # 현재 디렉토리 경로를 스택 최상위로부터 만든 뒤, tokens를 하나씩 내려간다
        current_dir = path_stack[-1]  # 스택 최상위 경로

        for i, token in enumerate(tokens):
            # 다음 경로
            new_path = os.path.join(current_dir, token)

            if i < len(tokens) - 1:
                # 마지막 토큰이 아니면 => 디렉토리
                os.makedirs(new_path, exist_ok=True)
                # current_dir 갱신
                current_dir = new_path
            else:
                # 마지막 토큰
                # 파일인지 폴더인지 판단
                if is_file(token):
                    # 파일
                    parent_dir = os.path.dirname(new_path)
                    os.makedirs(parent_dir, exist_ok=True)
                    open(new_path, 'w').close()
                else:
                    # 디렉토리
                    os.makedirs(new_path, exist_ok=True)
                    # depth 스택을 위해 current_dir 갱신
                    current_dir = new_path

        # 모든 tokens 처리가 끝난 후, path_stack 업데이트
        # (가장 마지막에 만든 디렉토리를 path_stack에 반영)
        if not is_file(tokens[-1]):
            # 마지막 토큰이 폴더라면 그 폴더를 스택에 추가
            # 만약 이미 depth+1 길이가 맞다면 교체
            if len(path_stack) == depth+1:
                path_stack.append(new_path)
            else:
                # 혹시 불일치하면 맞춰 pop 후 push
                while len(path_stack) > depth:
                    path_stack.pop()
                path_stack.append(new_path)

if __name__ == "__main__":
    main()
