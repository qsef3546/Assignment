
# Assignment

이 프로젝트는 FastAPI 프레임워크를 사용하며 JWT(JSON Web Tokens)를 사용한 인증을 하여 유저, 게시글 관리하는 프로젝트 입니다. 이 프로젝트에는 사용자 로그인, 토큰 생성 및 보호된 경로에 대한 JWT 인증 처리를 위한 미들웨어가 포함되어 있습니다.

## 설치

1. 저장소를 클론합니다.
2. 다음 내용을 포함한 `.env` 파일을 루트 디렉토리에 생성합니다:
   ```
   SECRET_KEY=your_secret_key
   ```
   - SECRET_KEY 는 secrets 모듈로 만들어 사용하였습니다.
3. 필요한 패키지를 설치합니다:
   ```
   pip install -r requirements.txt
   ```

## 요구 사항

프로젝트 종속성은 `requirements.txt` 파일에 나열되어 있습니다:

- `psycopg2-binary`
- `uvicorn`
- `fastapi`
- `pydantic`
- `sqlmodel`
- `pydantic_core`
- `python-jose[cryptography]`
- `python-dotenv`
- `pytest`
- `pymongo`


## JWT 인증 미들웨어

미들웨어는 보호된 경로에 대한 `Authorization` 헤더에서 JWT 토큰을 확인합니다. 토큰이 유효한 경우 사용자의 정보가 요청 상태에 첨부됩니다. 토큰이 유효하지 않거나 만료된 경우 적절한 오류 응답이 반환됩니다.

### 보호된 경로
다음 경로는 유효한 JWT 토큰이 필요합니다:
- `/auth/add_access_token`
- `/user/delete`
- `/user/put`
- `/board/insert`
- `/board/put`
- `/board/delete`

### 공개 경로
위에 나열되지 않은 모든 경로는 공개되며 JWT 토큰이 필요하지 않습니다.

## 유틸리티 함수

### `create_token(data: dict, expire_time: int) -> str`
주어진 데이터와 만료 시간을 사용하여 JWT 토큰을 생성합니다.

### `encoded_pw(pw: str) -> str`
SHA-256 해싱을 사용하여 주어진 비밀번호를 인코딩합니다.

## 오류 처리

프로젝트에는 잘못된 자격 증명, 만료된 토큰 및 잘못된 토큰 유형과 같은 다양한 인증 오류에 대한 오류 처리가 포함되어 있습니다.

## 사용 예시

1. **로그인**:
   ```bash
   curl -X POST "http://localhost:8000/auth/login" -d "username=user@example.com&password=yourpassword"
   ```

2. **액세스 토큰 추가**:
   ```bash
   curl -X POST "http://localhost:8000/auth/add_access_token" -H "Authorization: Bearer <your_refresh_token>"
   ```

## 로깅
요청 및 응답에 대한 로그가 데이터베이스에 삽입되어 추적 목적으로 사용됩니다.

## 각 폴더 및 파일 설명

### handler 폴더 (Router)

#### `auth_handler.py`
- Router = /auth
- 사용자 인증 및 JWT 토큰 생성과 관련된 API를 처리합니다.

#### `user_handler.py`
- Router = /user
- 사용자 관리와 관련된 API를 처리합니다. 사용자 등록, 정보 수정, 삭제 등이 가능합니다.

#### `board_handler.py`
- Router = /board
- 게시판 관련 기능을 처리하는 API를 포함합니다. 게시물 작성, 수정, 조회, 삭제 등이 가능합니다.

#### `response_handler.py`
- 응답 처리를 위한 유틸리티 함수를 포함합니다. 표준화된 오류 응답 등을 처리합니다.



### model 폴더

#### `board.py`
- 게시판 관련 데이터 모델을 정의합니다.

#### `log.py`
- 로그 데이터를 모델링하며, 각 요청 및 응답에 대한 로그를 데이터베이스에 기록합니다.

#### `mg_sqlconf.py`
- MongoDB 데이터베이스 설정을 포함합니다.

#### `pg_sqlconf.py`
- PostgreSQL 데이터베이스 설정을 포함합니다.

#### `user.py`
- 사용자 데이터를 모델링하며, 사용자 정보와 관련된 기능을 제공합니다.

### unit_test 폴더

#### `auth_test.py`
- 인증 관련 API를 테스트합니다. 로그인, 토큰 생성 및 유효성 검사 등을 포함합니다.

#### `board_test.py`
- 게시판 관련 API를 테스트합니다. 게시물 작성, 수정, 삭제 기능의 동작을 검증합니다.

#### `user_test.py`
- 사용자 관리 관련 API를 테스트합니다. 사용자 등록, 정보 수정, 삭제 기능의 동작을 검증합니다.

<br><br>

## 추가 구현 혹은 개선해야 되는 것
### 1. Refresh token Black list
- 'A' 유저가 로그아웃 후 유효기간이 남은 Refresh token 을 블랙리스트에 추가하여 Access token 재발급 할 수 없도록 해야할 필요가 있습니다.
- Redis 로  Refresh Token 만료 기간을 TTL로 잡아 Refresh token 을 추가 하는게 좋아보입니다.

### 2. Logger 추가
- mongo DB에 적재되는 로그외 각 함수별, DB 쿼리 별 로그를 logger 파일에 적재할 필요가 보입니다.
- 현재는 간단하게 보기 위하여 print 문으로 작성하였습니다.

### 3. Pagenation 성능개선
- 현재 게시판 목록에 대한 Pagenation 은 DB 쿼리시 offset(offset_number) 로 조회되도록 하였습니다. 
- 지금은 적은 양의 게시글이 있기에 성능에 크게 달라지진 않지만 많은 게시글이 쌓이면 성능이 안 좋아질 것으로 보여 offset() 보단 pk (column = no)나 특정 컬럼을 인덱스로 만들어 처리하는게 좋을 것 같습니다.

### 4. 코드 최적화
- 현재 최적화가 필요한 부분이 보입니다. 자주사용 되는 문법들을 함수화 하여 사용해야할 필요가 있습니다.


<br><br><br><br><br><br><br><br><br><br><br>

# 

이 프로젝트는 '비바이노베이션'을 위해서만 사용될 수 있습니다. 이 프로젝트의 일부 또는 전체를 비바이노베이션의 허가 없이 다른 용도로 사용하는 것은 금지되어 있습니다.

