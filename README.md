# Mattermost AI Translator

자동 AI 기반 메시지 번역 서비스 for Mattermost

Mattermost에서 메시지를 입력하면 자동으로 AI가 번역하여 채널에 다시 메시지를 게시합니다.

## 주요 기능

- 🤖 **AI 기반 자동 번역**: OpenAI GPT 또는 Anthropic Claude를 사용한 고품질 번역
- 🌐 **양방향 번역**: 한국어 ↔ 영어 자동 감지 및 번역
- 🔄 **다국어 지원**: 기타 언어는 한국어와 영어로 동시 번역
- 📝 **포맷 보존**: Markdown 형식 유지
- 🚫 **Bot 필터링**: 무한 루프 방지를 위한 Bot 메시지 자동 필터링
- 🐳 **Docker 지원**: 간편한 배포 및 운영
- ⚡ **Production-Ready**: 에러 처리, 로깅, 타임아웃 설정 포함

## 아키텍처

```
Mattermost Channel
      ↓
Outgoing Webhook
      ↓
FastAPI Translation Server
      ├─→ AI Model (OpenAI/Claude)
      └─→ Translation
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
│   ├── ai_client.py            # AI 번역 클라이언트 (litellm)
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
- OpenAI API Key 또는 Anthropic API Key
- Mattermost Server 접근 권한

## 설치 및 실행

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd Mattermost_autotranslate
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env
```

**필수 설정 항목:**

```env
# AI API Key (둘 중 하나 이상 필수)
OPENAI_API_KEY=sk-your-openai-api-key
# 또는
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# AI 모델 선택
AI_MODEL=gpt-4o-mini
# 또는
# AI_MODEL=claude-3-5-sonnet-20241022

# Mattermost Incoming Webhook URL (필수)
MATTERMOST_INCOMING_WEBHOOK_URL=https://your-mattermost.com/hooks/xxx
```

### 3-A. Docker로 실행 (권장)

```bash
# Docker Compose로 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 3-B. 로컬에서 실행

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

### 4. 서버 확인

서버가 정상적으로 실행되었는지 확인:

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

1. Mattermost에 로그인
2. **Main Menu** → **Integrations** → **Incoming Webhooks**
3. **Add Incoming Webhook** 클릭
4. 설정:
   - **Title**: AI Translator Incoming Webhook
   - **Description**: Receives translated messages
   - **Channel**: 번역 결과를 받을 채널 선택
5. **Save** 클릭
6. 생성된 **Webhook URL** 복사 → `.env` 파일의 `MATTERMOST_INCOMING_WEBHOOK_URL`에 설정

### 2. Outgoing Webhook 생성

1. Mattermost에 로그인
2. **Main Menu** → **Integrations** → **Outgoing Webhooks**
3. **Add Outgoing Webhook** 클릭
4. 설정:
   - **Title**: AI Translator Outgoing Webhook
   - **Description**: Sends messages to translation service
   - **Content Type**: `application/x-www-form-urlencoded`
   - **Channel**: 번역할 메시지를 감지할 채널 선택
   - **Trigger Words**: (비워두면 모든 메시지 번역)
     - 특정 단어로 트리거하려면 입력 (예: `translate`, `번역`)
   - **Trigger When**:
     - ✅ **First word matches a trigger word exactly**
     - 또는 ✅ **First word starts with a trigger word** (선택사항)
   - **Callback URLs**:
     - `http://your-server-ip:8000/mattermost/translate`
     - 예: `http://192.168.1.100:8000/mattermost/translate`
5. **Save** 클릭

**중요 참고사항:**
- Outgoing Webhook의 Callback URL은 외부에서 접근 가능한 IP 주소여야 합니다
- 로컬 테스트 시에는 같은 네트워크의 서버 IP를 사용하거나 ngrok 등의 터널링 서비스 사용
- Production 환경에서는 도메인과 HTTPS 사용 권장

### 3. Ngrok을 사용한 로컬 테스트 (선택사항)

로컬 개발 환경에서 외부 접근이 필요한 경우:

```bash
# ngrok 설치 후
ngrok http 8000
```

ngrok이 제공하는 HTTPS URL을 Outgoing Webhook의 Callback URL로 사용:
```
https://abc123.ngrok.io/mattermost/translate
```

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

**입력 (영어):**
```
Please review the pull request when you have time.
```

**출력 (한국어):**
```
시간이 되실 때 풀 리퀘스트를 검토해주세요.
```

## 환경 변수 상세 설명

| 변수명 | 필수 | 기본값 | 설명 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | 선택* | - | OpenAI API 키 |
| `ANTHROPIC_API_KEY` | 선택* | - | Anthropic API 키 |
| `AI_MODEL` | 아니오 | `gpt-4o-mini` | 사용할 AI 모델 |
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

**\* API 키는 OpenAI 또는 Anthropic 둘 중 하나 이상 필수**

## 지원 AI 모델

### OpenAI Models
- `gpt-4o` - 최신 GPT-4 Optimized
- `gpt-4o-mini` - 경제적인 GPT-4 (권장)
- `gpt-4-turbo` - GPT-4 Turbo
- `gpt-3.5-turbo` - GPT-3.5

### Anthropic Claude Models
- `claude-3-5-sonnet-20241022` - Claude 3.5 Sonnet (최신, 권장)
- `claude-3-opus-20240229` - Claude 3 Opus (최고 성능)
- `claude-3-sonnet-20240229` - Claude 3 Sonnet
- `claude-3-haiku-20240307` - Claude 3 Haiku (빠름)

## 문제 해결

### 번역이 작동하지 않음

1. **로그 확인:**
   ```bash
   docker-compose logs -f
   ```

2. **Health 체크:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **환경 변수 확인:**
   - API 키가 올바른지 확인
   - Webhook URL이 정확한지 확인

### Mattermost에서 메시지를 받지 못함

1. Outgoing Webhook의 Callback URL이 올바른지 확인
2. 서버가 Mattermost에서 접근 가능한지 확인
3. 방화벽 설정 확인

### 무한 루프 발생

- `IGNORED_USERNAMES`에 `ai-translator-bot`이 포함되어 있는지 확인
- Bot이 자신의 메시지를 다시 번역하지 않도록 설정되어 있어야 함

## 보안 고려사항

1. **API 키 보호**: `.env` 파일을 Git에 커밋하지 마세요
2. **HTTPS 사용**: Production에서는 HTTPS 사용 권장
3. **방화벽**: 필요한 포트만 개방
4. **인증**: Mattermost Token 검증 추가 고려

## 라이센스

MIT License

## 기여

이슈 및 Pull Request 환영합니다!

## 지원

문제가 발생하면 GitHub Issues에 등록해주세요.
