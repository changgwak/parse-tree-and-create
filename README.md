# parse-tree-and-create

아래는 **(1) `tree`를 사용하여 구조를 텍스트 파일로 만드는 방법**과  
**(2) 그 텍스트 파일을 이용해 같은 폴더/파일 구조를 새롭게 생성**하는 과정을 정리한 안내입니다.

---

## 1. 기존 디렉토리 구조를 `tree`로 텍스트 파일에 저장

1) **`tree` 설치 확인**  
   - 대부분의 리눅스/유닉스 계열에서는 `sudo apt-get install tree` 등으로 설치 가능.
   - macOS에서 Homebrew 사용 시 `brew install tree`  
   - Windows는 WSL 또는 Git Bash에 tree 패키지가 포함되기도 하고, 별도 설치도 가능.

2) **디렉토리 구조 출력**  
   예를 들어, 현재 디렉토리를 기준으로 구조를 보고 싶다면:
   ```bash
   tree
   ```
   - 결과는 터미널에 표시됩니다.

3) **구조를 텍스트 파일로 저장**  
   - 예: `project_tree.txt`라는 파일로 저장  
   ```bash
   tree --noreport --charset unicode > project_tree.txt
   ```

   or

   ```bash
   tree > project_tree.txt
   ```
   - `--noreport`: 마지막에 `XX directories, YY files` 같은 요약 제외  
   - `--charset unicode`: ‘├──’, ‘└──’ 같은 문자가 깨지지 않도록 유니코드 사용  
     (OS에 따라 `--charset=ASCII`나 `-C` 등 다른 옵션을 시도)

   - **주의**: `tree -f` 옵션은 “풀 경로”가 찍혀서 `~/mydir/...` 식으로 경로가 중복될 수 있으므로,  
     보통은 **생략**해서 “상대 경로만” 나오게 하는 것이 파싱하기 쉽습니다.

4) 이렇게 하면 `project_tree.txt` 안에 디렉토리 구조가 트리 형태(‘├──’, ‘└──’ 등)로 기록됩니다.

---

## 2. 텍스트 파일(`project_tree.txt`)을 이용해 같은 구조 생성

1) **파이썬 스크립트 준비**  
   - 아래 **예시 코드**를 `parse_tree_and_create.py` 같은 이름으로 저장합니다.
   - 여기서는 “(슬래시 없는) 일반적인 `tree` 출력”을 가정한 비교적 간단한 파서를 예시로 들겠습니다.


> - **더 복잡한 상황**(예: 트리 라인에 `/`가 들어간 복합 경로가 있거나, 확장자가 없지만 파일인 것이 있으면)을 처리하려면 코드를 추가 수정해야 합니다.  
> - 위 코드는 **“tree 기본 출력(상대 경로)”**을 전제로 하여, `.sh`, `.txt`, `.cpp` 등 **마침표가 있는 파일**을 “파일”로 보고, 나머지를 전부 폴더로 처리합니다.

2) **실행 권한 부여**  
   ```bash
   chmod +x parse_tree_and_create.py
   ```
   (Windows라면 권한 부분은 넘어가도 됨)

3) **실행**  
   ```bash
   ./parse_tree_and_create.py
   ```
   - 현재 디렉토리에 `project_tree.txt`가 있다고 가정.  
   - 스크립트가 끝나면, 현 위치(또는 스크립트와 같은 폴더) 안에 `tree` 구조와 동일하게 **디렉토리와 빈 파일**이 생성됩니다.

4) **결과 확인**  
   ```bash
   tree
   ```
   - 실제 복제된 폴더 구조가 제대로 보이는지 확인할 수 있습니다.  
   - 파일은 전부 **빈 파일**(`0byte`)로 생성됩니다.

---

## 3. 정리

1. **원본 디렉토리** → `tree --noreport --charset unicode > project_tree.txt`  
   (필요하다면 `cd`로 해당 디렉토리로 이동해서 `.` 기준으로 트리를 찍는다.)  

2. **새 디렉토리**(아무것도 없는 곳)에서  
   - 위 `project_tree.txt`를 가져옴 → `parse_tree_and_create.py` 스크립트 실행 → **동일한 폴더 구조와 빈 파일** 생성.

이 과정을 통해, 한 디렉토리의 구조를 텍스트 형태로 백업했다가 **다른 곳에서 동일 구조를 복원**할 수 있습니다.  