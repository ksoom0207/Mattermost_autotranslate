# Mattermost AI Translator

자동 AI 기반 메시지 번역 서비스 for Mattermost

Mattermost에서 메시지를 입력하면 자동으로 AI가 번역하여 채널에 다시 메시지를 게시합니다.

## 주요 기능

- 🤖 **AI 기반 자동 번역**: LiteLLM Proxy를 통한 로컬/원격 AI 모델 사용
- 🌐 **양방향 번역**: 한국어 ↔ 영어 자동 감지 및 번역
- 🔄 **다국어 지원**: 기타 언어는 한국어와 영어로 동시 번역
- 📝 **포맷 보존**: Markdown 형식 유지
- 🚫 **Bot 필터링**: 무한 루프 방지를 위한 Bot 메시지 자동 필터링
- 🔌 **LiteLLM Proxy 연동**: OpenAI SDK v1을 사용한 표준 API 호출
- 🐳 **Docker 지원**: 간편한 배포 및 운영
- ⚡ **Production-Ready**: 에러 처리, 로깅, 타임아웃 설정 포함

## 아키텍처

```
Mattermost Channel
      ↓
Outgoing Webhook
      ↓
FastAPI Translation Server
      ↓
OpenAI SDK v1 (client)
      ↓
LiteLLM Proxy (localhost:4000)
      ↓
AI Model (Local LLM, OpenAI, Claude, etc.)
      ↓
Translation Result
      ↓
Incoming Webhook
      ↓
Mattermost Channel (번역 결과)
```

## 프로젝트 구조

```
Mattermost_autotranslate/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 애플리케이션
│   ├── config.py               # 환경 변수 및 설정
│   ├── schemas.py              # Pydantic 데이터 모델
│   ├── ai_client.py            # AI 번역 클라이언트 (OpenAI SDK)
│   ├── mattermost_client.py    # Mattermost Webhook 클라이언트
│   └── utils.py                # 유틸리티 함수
├── requirements.txt            # Python 의존성
├── Dockerfile                  # Docker 이미지 빌드
├── docker-compose.yml          # Docker Compose 설정
├── .env.example               # 환경 변수 템플릿
├── .gitignore                 # Git 제외 파일
└── README.md                  # 이 문서
```

## 사전 요구사항

- Python 3.10 이상 (로컬 실행 시)
- Docker 및 Docker Compose (Docker 실행 시)
- **LiteLLM Proxy 서버** (로컬 또는 원격)
- Mattermost Server 접근 권한

## 빠른 시작

### 1. LiteLLM Proxy 서버 실행

먼저 LiteLLM Proxy 서버를 실행해야 합니다.

**옵션 A: 간단한 로컬 실행 (테스트용)**

```bash
# LiteLLM 설치
pip install litellm[proxy]

# OpenAI 모델로 프록시 시작
export OPENAI_API_KEY=sk-your-key
litellm --model gpt-4o-mini --port 4000

# 또는 Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-your-key
litellm --model claude-3-5-sonnet-20241022 --port 4000
```

**옵션 B: config.yaml 사용 (권장)**

```yaml
# config.yaml
model_list:
  - model_name: translator-local
    litellm_params:
      model: gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY

  - model_name: translator-claude
    litellm_params:
      model: claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

general_settings:
  master_key: dummy-key  # API key for proxy authentication
```

```bash
# config.yaml로 프록시 시작
litellm --config config.yaml --port 4000
```

**옵션 C: Ollama 등 로컬 LLM 사용**

```bash
# Ollama 실행 (별도 터미널)
ollama serve

# LiteLLM을 Ollama에 연결
litellm --model ollama/llama3.2 --port 4000
```

### 2. 프로젝트 설정

```bash
# 프로젝트 클론
git clone <repository-url>
cd Mattermost_autotranslate

# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env
```

**필수 설정 (.env):**

```env
# LiteLLM Proxy 설정
LITELLM_API_BASE=http://localhost:4000
LITELLM_API_KEY=dummy-key

# 모델명 (LiteLLM Proxy에 설정한 이름)
AI_MODEL=translator-local

# Mattermost Incoming Webhook URL (필수!)
MATTERMOST_INCOMING_WEBHOOK_URL=https://your-mattermost.com/hooks/xxx
```

### 3. 번역 서버 실행

**Docker로 실행 (권장):**

```bash
# Docker Compose로 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

**로컬에서 실행:**

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python -m app.main
# 또는
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Health Check

```bash
curl http://localhost:8000/health
```

응답:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "ai_configured": true
}
```

## Mattermost 설정

### 1. Incoming Webhook 생성

1. Mattermost → **Main Menu** → **Integrations** → **Incoming Webhooks**
2. **Add Incoming Webhook** 클릭
3. 채널 선택 후 생성
4. **Webhook URL** 복사 → `.env`의 `MATTERMOST_INCOMING_WEBHOOK_URL`에 설정

### 2. Outgoing Webhook 생성

1. Mattermost → **Main Menu** → **Integrations** → **Outgoing Webhooks**
2. **Add Outgoing Webhook** 클릭
3. 설정:
   - **Content Type**: `application/x-www-form-urlencoded`
   - **Channel**: 번역할 채널 선택
   - **Trigger Words**: 비워두기 (모든 메시지 번역)
   - **Callback URL**: `http://your-server-ip:8000/mattermost/translate`
4. **Save** 클릭

**참고:**
- Callback URL은 Mattermost에서 접근 가능한 IP여야 합니다
- 로컬 테스트: ngrok 사용 (`ngrok http 8000`)
- Production: 도메인 + HTTPS 권장

## 사용 방법

### 기본 사용

1. 설정한 Mattermost 채널에 메시지 입력
2. AI가 자동으로 언어 감지 및 번역
3. 번역 결과가 `ai-translator-bot` 이름으로 채널에 게시됨

### 번역 규칙

| 원본 언어 | 번역 결과 |
|---------|----------|
| 한국어 | 영어로 번역 |
| 영어 | 한국어로 번역 |
| 기타 언어 | 한국어 + 영어 (둘 다) |

### 예시

**입력 (한국어):**
```
안녕하세요! 오늘 회의는 3시에 시작합니다.
```

**출력 (영어):**
```
Hello! Today's meeting starts at 3 PM.
```

## 환경 변수 상세 설명

| 변수명 | 필수 | 기본값 | 설명 |
|--------|------|--------|------|
| `LITELLM_API_BASE` | **필수** | `http://localhost:4000` | LiteLLM Proxy 서버 URL |
| `LITELLM_API_KEY` | **필수** | `dummy-key` | LiteLLM Proxy API 키 |
| `AI_MODEL` | 아니오 | `translator-local` | LiteLLM Proxy에 설정된 모델명 |
| `AI_TEMPERATURE` | 아니오 | `0.3` | AI 생성 온도 (0.0-2.0) |
| `AI_MAX_TOKENS` | 아니오 | `2000` | 최대 토큰 수 |
| `AI_TIMEOUT` | 아니오 | `30` | AI API 타임아웃 (초) |
| `MATTERMOST_INCOMING_WEBHOOK_URL` | **필수** | - | Mattermost Incoming Webhook URL |
| `MATTERMOST_BOT_USERNAME` | 아니오 | `ai-translator-bot` | Bot 표시 이름 |
| `MATTERMOST_BOT_ICON_URL` | 아니오 | - | Bot 아이콘 URL |
| `IGNORED_USERNAMES` | 아니오 | `ai-translator-bot,...` | 무시할 사용자명 (쉼표 구분) |
| `SERVER_HOST` | 아니오 | `0.0.0.0` | 서버 호스트 |
| `SERVER_PORT` | 아니오 | `8000` | 서버 포트 |
| `LOG_LEVEL` | 아니오 | `INFO` | 로그 레벨 |

## LiteLLM Proxy 설정 예시

### OpenAI GPT 모델 사용

```yaml
# config.yaml
model_list:
  - model_name: translator-local
    litellm_params:
      model: gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY

general_settings:
  master_key: dummy-key
```

### Anthropic Claude 모델 사용

```yaml
# config.yaml
model_list:
  - model_name: translator-local
    litellm_params:
      model: claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

general_settings:
  master_key: dummy-key
```

### Ollama 로컬 LLM 사용

```yaml
# config.yaml
model_list:
  - model_name: translator-local
    litellm_params:
      model: ollama/llama3.2
      api_base: http://localhost:11434

general_settings:
  master_key: dummy-key
```

### 여러 모델 동시 지원

```yaml
# config.yaml
model_list:
  - model_name: translator-gpt
    litellm_params:
      model: gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY

  - model_name: translator-claude
    litellm_params:
      model: claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: translator-local
    litellm_params:
      model: ollama/llama3.2
      api_base: http://localhost:11434

general_settings:
  master_key: dummy-key
```

번역 서버 `.env`에서 원하는 모델 선택:
```env
AI_MODEL=translator-gpt  # 또는 translator-claude, translator-local
```

## 문제 해결

### 번역이 작동하지 않음

1. **로그 확인:**
   ```bash
   docker-compose logs -f
   ```

2. **LiteLLM Proxy 확인:**
   ```bash
   curl http://localhost:4000/health
   ```

3. **번역 서버 Health 체크:**
   ```bash
   curl http://localhost:8000/health
   ```

### LiteLLM Proxy 연결 오류

- `LITELLM_API_BASE`가 정확한지 확인
- LiteLLM Proxy가 실행 중인지 확인
- 포트 번호가 일치하는지 확인 (기본: 4000)

### Mattermost Webhook 오류

- Incoming Webhook URL이 정확한지 확인
- Outgoing Webhook Callback URL이 접근 가능한지 확인
- 방화벽 설정 확인

### 무한 루프 발생

- `IGNORED_USERNAMES`에 `ai-translator-bot`이 포함되어 있는지 확인
- Bot 자신의 메시지를 무시하도록 설정

## Docker Compose로 전체 스택 실행

LiteLLM Proxy와 번역 서버를 함께 실행:

```yaml
# docker-compose.yml
version: '3.8'

services:
  litellm-proxy:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    command: ["--model", "gpt-4o-mini", "--port", "4000"]
    networks:
      - translator-network

  mattermost-translator:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - LITELLM_API_BASE=http://litellm-proxy:4000
    depends_on:
      - litellm-proxy
    networks:
      - translator-network

networks:
  translator-network:
    driver: bridge
```

```bash
# 전체 스택 실행
export OPENAI_API_KEY=sk-your-key
docker-compose up -d
```

## 기술 스택

- **FastAPI**: 고성능 비동기 웹 프레임워크
- **OpenAI SDK v1**: LiteLLM Proxy 연동
- **LiteLLM**: 통합 LLM 프록시 서버
- **Pydantic**: 데이터 검증 및 설정 관리
- **HTTPX**: 비동기 HTTP 클라이언트
- **Docker**: 컨테이너화 및 배포

## 라이센스

MIT License

## 기여

이슈 및 Pull Request 환영합니다!

## 참고 자료

- [LiteLLM 공식 문서](https://docs.litellm.ai/)
- [Mattermost Webhooks](https://docs.mattermost.com/developer/webhooks.html)
- [OpenAI SDK Python](https://github.com/openai/openai-python)
