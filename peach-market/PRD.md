# 피치마켓(Peach Market) — 개발 계획서 / PRD

> 중고 거래 서비스 "피치마켓" 풀스택 클론 프로젝트.
> 노마드코더 *캐럿마켓 클론코딩* 커리큘럼(Next.js 14 · Tailwind · Prisma, 총 148강) 구조를 참고해
> Claude Code가 순차 실행할 수 있도록 최대한 세분화한 개발 계획서.

---

## 0. 이 문서를 읽는 Claude Code에게 (실행 지침)

- **한 번에 한 Phase씩** 진행한다. Phase는 `Phase 0 → Phase 15` 순서로 의존성이 있다.
- 각 Phase는 **작업 체크리스트(Tasks)** 와 **완료 기준(Acceptance Criteria)** 을 가진다. 완료 기준을 모두 만족해야 다음 Phase로 넘어간다.
- 각 Phase 종료 시 **커밋**한다. 커밋 메시지는 `feat(phaseN): ...` 형식.
- 새 의존성 설치, DB 스키마 변경, 마이그레이션은 **명령어를 그대로 실행**하고 결과를 확인한다.
- UI는 모바일 우선(mobile-first, 최대 폭 `max-w-screen-sm` 중앙 정렬)으로 만든다. 당근/중고거래 앱은 모바일 웹뷰 기준이다.
- 타입은 엄격하게(`strict: true`) 유지하고, `any`를 남발하지 않는다.
- 이 문서에 명세가 부족한 세부 UI 텍스트/색상은 "피치(복숭아)" 브랜드 톤(메인 컬러: 복숭아빛 `#FF8B7B`~`#FF6F61`, 포인트 오렌지)으로 자유롭게 채운다.

---

## 1. 제품 개요

| 항목 | 내용 |
|---|---|
| 서비스명 | 피치마켓 (Peach Market) |
| 한 줄 정의 | 우리 동네 중고 직거래 + 동네생활 커뮤니티 풀스택 웹앱 |
| 타깃 | 모바일 웹 사용자 (반응형, 모바일 우선) |
| 핵심 가치 | 가까운 동네 이웃과 안전하고 빠른 중고거래 |
| 참고 모델 | 당근마켓 / 노마드코더 캐럿마켓 |

### 1.1 핵심 사용자 스토리
1. 방문자는 **전화번호 또는 이메일/GitHub 계정**으로 가입·로그인할 수 있다.
2. 사용자는 **판매 상품을 사진과 함께 등록**하고, 목록/상세를 볼 수 있다.
3. 사용자는 상품을 **검색**하고, 관심 상품을 **찜(좋아요)** 할 수 있다.
4. 사용자는 판매자와 **1:1 실시간 채팅**으로 거래를 문의한다.
5. 사용자는 **동네생활** 게시글을 쓰고, 댓글·궁금해요로 소통한다.
6. 사용자는 **내 프로필**에서 판매내역·구매내역·찜 목록을 관리한다.

---

## 2. 기술 스택

| 레이어 | 선택 | 비고 |
|---|---|---|
| 프레임워크 | **Next.js 14 (App Router)** | Server Components + Server Actions 중심 |
| 언어 | **TypeScript** (strict) | |
| 스타일 | **Tailwind CSS** | `@tailwindcss/forms` 플러그인 |
| DB ORM | **Prisma** | |
| DB | 개발: **SQLite** → 운영: **PostgreSQL** (Supabase/Neon) | 마이그레이션 호환 유지 |
| 인증 세션 | **iron-session** (쿠키 기반) | 비번 해시 `bcrypt` |
| 폼 검증 | **Zod** + `useActionState`(React 19)/Server Action | |
| 이미지 저장 | **Cloudflare Images** (direct upload URL) | 대체: Supabase Storage |
| 실시간 채팅 | **Supabase Realtime** | 대체: Pusher |
| 배포 | **Vercel** | |
| 패키지 매니저 | **npm** | |

> 이미지/실시간 외부 서비스 키가 없으면 해당 Phase는 **목(mock)/로컬 파일 업로드**로 우선 구현하고, 키 확보 후 교체하도록 TODO를 남긴다.

---

## 3. 최종 라우트 구조 (목표)

```
app/
  (auth)/
    create-account/page.tsx     # 회원가입
    login/page.tsx              # 로그인
    sms/page.tsx                # 전화번호 인증 로그인
    github/
      start/route.ts            # GitHub OAuth 시작
      complete/route.ts         # GitHub OAuth 콜백
  (tabs)/
    (home)/
      page.tsx                  # 상품 목록 (홈)
      @modal/(...)products/[id]/page.tsx  # (선택) 인터셉트 모달
    life/page.tsx               # 동네생활 목록
    chat/page.tsx               # 채팅방 목록
    live/page.tsx               # 라이브(선택)
    profile/page.tsx            # 나의 피치
    layout.tsx                  # 하단 탭바
  products/
    [id]/page.tsx               # 상품 상세
    [id]/edit/page.tsx          # 상품 수정
    add/page.tsx                # 상품 등록
  posts/
    [id]/page.tsx               # 동네생활 글 상세
    add/page.tsx                # 글 작성
  chats/
    [id]/page.tsx               # 채팅방
  search/page.tsx               # 검색
lib/
  db.ts                         # Prisma client 싱글턴
  session.ts                    # iron-session 헬퍼
  utils.ts
components/
  ...
prisma/
  schema.prisma
middleware.ts                   # 인증/권한 보호
```

---

## 4. 데이터 모델 (Prisma 목표 스키마)

> Phase 2에서 최소 모델로 시작해 Phase가 진행되며 점진적으로 확장한다. 아래는 **최종 목표**.

```prisma
model User {
  id        Int      @id @default(autoincrement())
  username  String   @unique
  email     String?  @unique
  password  String?
  phone     String?  @unique
  github_id String?  @unique
  avatar    String?
  bio       String?
  created_at DateTime @default(now())
  updated_at DateTime @updatedAt

  tokens     SMSToken[]
  products   Product[]
  posts      Post[]
  comments   Comment[]
  postLikes  PostLike[]
  productLikes ProductLike[]
  // 채팅
  chatRooms  ChatRoom[]
  messages   Message[]
}

model SMSToken {
  id      Int      @id @default(autoincrement())
  token   String   @unique
  user    User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId  Int
  created_at DateTime @default(now())
}

model Product {
  id          Int      @id @default(autoincrement())
  title       String
  price       Int
  description String
  photo       String
  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId      Int
  created_at  DateTime @default(now())
  updated_at  DateTime @updatedAt
  likes       ProductLike[]
}

model ProductLike {
  product   Product @relation(fields: [productId], references: [id], onDelete: Cascade)
  productId Int
  user      User    @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId    Int
  created_at DateTime @default(now())
  @@id(name: "id", [productId, userId])
}

model Post {
  id          Int      @id @default(autoincrement())
  title       String
  description String?
  views       Int      @default(0)
  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId      Int
  created_at  DateTime @default(now())
  updated_at  DateTime @updatedAt
  comments    Comment[]
  likes       PostLike[]
}

model Comment {
  id        Int    @id @default(autoincrement())
  payload   String
  user      User   @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId    Int
  post      Post   @relation(fields: [postId], references: [id], onDelete: Cascade)
  postId    Int
  created_at DateTime @default(now())
}

model PostLike {
  post    Post @relation(fields: [postId], references: [id], onDelete: Cascade)
  postId  Int
  user    User @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId  Int
  created_at DateTime @default(now())
  @@id(name: "id", [postId, userId])
}

model ChatRoom {
  id        String   @id @default(cuid())
  users     User[]
  messages  Message[]
  created_at DateTime @default(now())
  updated_at DateTime @updatedAt
}

model Message {
  id       Int      @id @default(autoincrement())
  payload  String
  room     ChatRoom @relation(fields: [chatRoomId], references: [id], onDelete: Cascade)
  chatRoomId String
  user     User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId   Int
  created_at DateTime @default(now())
  updated_at DateTime @updatedAt
}
```

---

## 5. 개발 Phase (세분화)

각 Phase는 강의 섹션에 대응한다. **번호 순서대로** 진행.

---

### Phase 0 — 프로젝트 셋업 (Setup)

**목표:** 실행 가능한 Next.js 14 + TS + Tailwind 스캐폴드.

**Tasks**
- [ ] `npx create-next-app@latest peach-market` (TypeScript, ESLint, Tailwind, App Router, `src/` 사용 안 함, import alias `@/*`) — 이미 이 레포 안에서 진행하면 `peach-market/` 하위에 앱 생성.
- [ ] 불필요한 보일러플레이트(`page.tsx` 기본 내용, 글로벌 CSS 데모) 정리.
- [ ] `app/globals.css`에 Tailwind 지시문만 남기고 기본 배경/폰트(모바일 우선) 세팅.
- [ ] 루트 `layout.tsx`에 `<body className="bg-neutral-900 text-white max-w-screen-sm mx-auto ...">` 형태로 모바일 컨테이너 구성(디자인은 이후 조정).
- [ ] `prettier` + `prettier-plugin-tailwindcss` 설치·설정.
- [ ] `.env`, `.env.example` 생성 및 `.gitignore` 확인.
- [ ] `npm run dev` 정상 구동 확인.

**Acceptance Criteria**
- `npm run dev` 시 에러 없이 홈 화면 렌더.
- `npm run build` 성공.
- TypeScript strict 통과.

---

### Phase 1 — 디자인/Tailwind 워밍업 (Tailwind Tour & Practice)

**목표:** 로그인 화면과 홈 목록의 **정적 UI**를 Tailwind로 완성 (데이터 없이 하드코딩).

**Tasks**
- [ ] `@tailwindcss/forms` 설치 및 `tailwind.config.ts` 플러그인 등록.
- [ ] 공통 UI 컴포넌트 작성:
  - [ ] `components/input.tsx` — label/errors/name/type 지원, 재사용 인풋.
  - [ ] `components/button.tsx` — loading 상태(비활성) 지원.
  - [ ] `components/social-login.tsx` — GitHub/전화 로그인 버튼(추후 링크 연결).
- [ ] `/login`, `/create-account` 화면 정적 마크업 (로고 "🍑 피치마켓", 인풋, 버튼).
- [ ] 홈 `(home)/page.tsx` 상품 카드 리스트 정적 마크업 (이미지 자리, 제목, 가격, 동네, 시간).
- [ ] 하단 탭바 `(tabs)/layout.tsx`: 홈 / 동네생활 / 채팅 / 라이브 / 나의피치 아이콘 (`heroicons` 설치).
- [ ] 플로팅 "＋" 글쓰기 버튼.

**Acceptance Criteria**
- 로그인/회원가입/홈이 모바일 폭에서 깔끔히 렌더.
- 하단 탭바가 모든 `(tabs)` 라우트에서 고정 노출.

---

### Phase 2 — 데이터베이스 셋업 (Database Setup)

**목표:** Prisma + SQLite 연결, `User`/`Product` 최소 모델 마이그레이션.

**Tasks**
- [ ] `npm i prisma -D` / `npm i @prisma/client`, `npx prisma init --datasource-provider sqlite`.
- [ ] `prisma/schema.prisma`에 최소 `User`, `Product` 모델 정의(§4의 부분집합).
- [ ] `lib/db.ts` — Prisma Client **싱글턴**(개발 HMR 중복 방지) 작성.
- [ ] `npx prisma migrate dev --name init` 실행 → `dev.db` 생성 확인.
- [ ] (선택) `prisma studio`로 데이터 확인.

**Acceptance Criteria**
- 마이그레이션 성공, `@prisma/client` 타입 생성.
- 서버 코드에서 `db.user.findMany()` 호출 시 빈 배열 반환(에러 없음).

---

### Phase 3 — 폼 & 검증 (React Hook Form → Server Actions + Zod)

**목표:** 회원가입 폼을 **Server Action + Zod**로 검증·에러 표시.

**Tasks**
- [ ] `npm i zod`.
- [ ] `app/(auth)/create-account/actions.ts` — `"use server"` Server Action.
- [ ] Zod 스키마: `username`(3~10자), `email`(형식), `password`(4자+, 정규식), `confirm_password`(일치 `refine`), 커스텀 에러 메시지(한글).
- [ ] `useActionState`로 클라이언트 폼과 연결, `Input`의 `errors` 표시.
- [ ] 중복 검사: username/email 존재 여부 `superRefine` + DB 조회.
- [ ] 검증 통과 시 `bcrypt` 해시 후 `User` 생성.

**Acceptance Criteria**
- 잘못된 입력 → 필드별 한글 에러 노출, DB 미저장.
- 정상 입력 → 유저 생성, 해시된 비번 저장 확인.

---

### Phase 4 — 인증: 세션 & 로그인 (Authentication)

**목표:** iron-session 기반 로그인/로그아웃, 세션 유지.

**Tasks**
- [ ] `npm i iron-session`. `COOKIE_PASSWORD` env(32자+) 생성.
- [ ] `lib/session.ts` — `getSession()`(쿠키명 `peach`, `SessionContent { id?: number }`).
- [ ] 회원가입 성공 시 세션에 `id` 저장 후 `redirect("/profile")`.
- [ ] `/login` Server Action: 이메일 존재 확인 → `bcrypt.compare` → 세션 저장.
- [ ] 로그아웃 액션: `session.destroy()` 후 `/login` 리다이렉트.
- [ ] `/profile`에서 `getSession()`으로 로그인 유저 표시.

**Acceptance Criteria**
- 로그인 후 새로고침해도 세션 유지.
- 로그아웃 시 세션 소멸, 보호 페이지 접근 차단.

---

### Phase 5 — 전화번호(SMS) 인증 로그인 (Streams/Token 방식)

**목표:** 전화번호 → 인증번호(토큰) → 로그인 2단계 폼.

**Tasks**
- [ ] `/sms/page.tsx` — 2단계 폼(1단계 전화번호, 2단계 토큰). `useActionState`로 `token` 단계 토글.
- [ ] 전화번호 검증: `libphonenumber-js`로 KR 유효성.
- [ ] 6자리 랜덤 토큰 생성 → `SMSToken` 저장(기존 유저 토큰 삭제 후 재발급). 유저 없으면 phone으로 생성.
- [ ] (외부 SMS API 키 없으면) 콘솔에 토큰 출력 + 화면 안내 문구로 대체(TODO 표기).
- [ ] 토큰 검증 성공 → 세션 저장 → `/profile`.

**Acceptance Criteria**
- 유효 전화번호 입력 시 토큰 발급, 잘못된 토큰 거부.
- 올바른 토큰 입력 시 로그인 완료.

---

### Phase 6 — 소셜 로그인 (GitHub OAuth)

**목표:** GitHub OAuth로 로그인/가입.

**Tasks**
- [ ] GitHub OAuth App 등록 안내(TODO: `GITHUB_CLIENT_ID/SECRET`), 콜백 `.../github/complete`.
- [ ] `app/(auth)/github/start/route.ts` — authorize URL로 리다이렉트(`scope=read:user,user:email`).
- [ ] `.../github/complete/route.ts` — code→access_token 교환 → `/user`, `/user/emails` 조회.
- [ ] `github_id`로 기존 유저 조회, 없으면 생성(username 충돌 회피, avatar 저장) → 세션 저장.
- [ ] `social-login.tsx`의 GitHub 버튼을 `/github/start`로 연결.

**Acceptance Criteria**
- GitHub 계정으로 최초 로그인 시 유저 자동 생성, 재로그인 시 동일 유저 매칭.

---

### Phase 7 — 권한 & 미들웨어 (Authorization)

**목표:** 비로그인 접근 차단, 로그인 유저의 인증 페이지 접근 차단.

**Tasks**
- [ ] `middleware.ts` — public 경로 화이트리스트(`/`, `/login`, `/create-account`, `/sms`, `/github/*`).
- [ ] 세션 쿠키 존재 여부로 분기: 비로그인+보호경로 → `/login`, 로그인+공개(auth)경로 → `/profile`.
- [ ] `matcher`로 정적파일/`_next` 제외.
- [ ] Edge 런타임 제약 고려(세션 쿠키만 확인, DB 접근 X).

**Acceptance Criteria**
- 로그아웃 상태에서 `/products/add` 접근 → `/login` 이동.
- 로그인 상태에서 `/login` 접근 → `/profile` 이동.

---

### Phase 8 — 상품 CRUD (Products)

**목표:** 상품 등록/목록/상세/수정/삭제 + 이미지 업로드.

**Tasks**
- [ ] **목록** `(home)/page.tsx`: `db.product.findMany`(최신순, select 최적화) → `ListProduct` 카드 컴포넌트.
- [ ] **상세** `products/[id]/page.tsx`: `generateMetadata`, 판매자 정보, 가격, 설명, "채팅하기" 버튼. 본인 상품이면 수정/삭제 버튼.
- [ ] **등록** `products/add/page.tsx`: 이미지 미리보기(`URL.createObjectURL`), title/price/description, Server Action으로 생성 후 `redirect(/products/{id})`.
- [ ] **이미지 업로드**: Cloudflare Images direct-upload URL 발급 route → 클라 업로드 → 최종 URL만 DB 저장. (키 없으면 `public/uploads` 로컬 저장으로 대체, TODO 표기.)
- [ ] **수정** `products/[id]/edit/page.tsx`: 본인 확인, 기존 값 프리필, 업데이트 액션.
- [ ] **삭제**: 본인 확인 후 삭제 → 홈 리다이렉트.
- [ ] **찜(좋아요)**: `ProductLike` 토글 Server Action + `revalidateTag`/optimistic UI.

**Acceptance Criteria**
- 상품 등록→상세 노출→수정→삭제 전 과정 동작.
- 타인 상품 수정/삭제 UI 미노출 및 서버단 차단.
- 이미지가 카드/상세에 정상 표시.

---

### Phase 9 — 검색 (Search)

**목표:** 상품 제목/설명 검색.

**Tasks**
- [ ] `/search/page.tsx` 검색 인풋(폼 제출 또는 `searchParams`).
- [ ] `db.product.findMany({ where: { OR: [{title contains}, {description contains}] } })`.
- [ ] 결과 없음/입력 전 empty state.
- [ ] (선택) 최근 검색어 로컬스토리지.

**Acceptance Criteria**
- 키워드로 관련 상품 필터링, 대소문자/부분일치 처리.

---

### Phase 10 — 동네생활 (게시글/댓글/궁금해요)

**목표:** 커뮤니티 글 CRUD + 댓글 + 좋아요(궁금해요) + 조회수.

**Tasks**
- [ ] `Post`, `Comment`, `PostLike` 모델 마이그레이션.
- [ ] **목록** `life/page.tsx`: 최신순, 작성자/조회수/좋아요/댓글수 표시.
- [ ] **작성** `posts/add/page.tsx`: title/description Server Action.
- [ ] **상세** `posts/[id]/page.tsx`: 조회수 증가(`update views`), `unstable_cache`로 좋아요 상태/카운트 캐싱.
- [ ] **궁금해요(좋아요)**: Server Action + `revalidateTag(likeStatus-{id})` + `useOptimistic`.
- [ ] **댓글**: 목록 + 작성 폼(Server Action), optimistic 추가, 본인 댓글 삭제.

**Acceptance Criteria**
- 글 작성→상세→조회수 증가→좋아요 토글→댓글 작성 동작.
- 좋아요/댓글이 낙관적 업데이트로 즉시 반영.

---

### Phase 11 — 프로필 (Profile)

**목표:** 나의 피치(마이페이지) — 정보 + 판매내역/구매내역/찜.

**Tasks**
- [ ] `profile/page.tsx`: 아바타/username/bio, 로그아웃 버튼.
- [ ] 탭 또는 섹션: 내 판매상품, 내가 찜한 상품, 내가 쓴 글.
- [ ] (선택) `profile/edit` — bio/avatar 수정.

**Acceptance Criteria**
- 로그인 유저의 활동 데이터가 정확히 필터링되어 노출.

---

### Phase 12 — 실시간 채팅 (Chat)

**목표:** 상품 상세의 "채팅하기" → 1:1 채팅방, 실시간 메시지.

**Tasks**
- [ ] `ChatRoom`, `Message` 모델 마이그레이션.
- [ ] "채팅하기" 액션: 두 유저의 기존 방 조회, 없으면 생성 → `/chats/{id}`.
- [ ] `chat/page.tsx`(채팅방 목록): 마지막 메시지 미리보기, 상대 아바타.
- [ ] `chats/[id]/page.tsx`: 과거 메시지 로드 + 입력창. 본인/상대 말풍선 좌우 구분.
- [ ] **실시간**: Supabase Realtime 채널 구독으로 새 메시지 수신/표시(키 없으면 폴링 or mock, TODO).
- [ ] 메시지 전송: DB 저장 + optimistic 추가 + 채널 broadcast.
- [ ] 접근 제어: 방 참여자만 입장 가능.

**Acceptance Criteria**
- 두 계정으로 실시간 주고받기(또는 새로고침 없이 표시) 동작.
- 무관한 유저의 방 접근 차단.

---

### Phase 13 — 이미지 최적화 (Cloudflare / next/image)

**목표:** 이미지 변형(variants)과 `next/image` 최적화.

**Tasks**
- [ ] `next.config`의 `images.remotePatterns`에 이미지 호스트 등록.
- [ ] Cloudflare Images variants(썸네일/공개) URL 규칙 적용, 카드=썸네일 / 상세=원본.
- [ ] `next/image` `sizes`/`priority`/blur placeholder 적용.

**Acceptance Criteria**
- 목록/상세 이미지가 적절한 해상도로 로드, CLS 최소화.

---

### Phase 14 — 캐싱 & ISR (NextJS Deep Dive / Incremental Static Regeneration)

**목표:** 데이터 캐싱 전략과 정적 재생성 적용.

**Tasks**
- [ ] 상품 상세: `unstable_cache`/`revalidate`로 캐싱, 변경 시 `revalidatePath`/`revalidateTag` 무효화.
- [ ] 홈 목록: 적절한 `revalidate` 주기(예: 60초) 또는 태그 기반 무효화.
- [ ] `generateStaticParams`로 인기 상품 사전 렌더(선택).
- [ ] `loading.tsx`/`error.tsx`/Suspense 스켈레톤 정비.

**Acceptance Criteria**
- 데이터 변경 후 관련 페이지가 재검증되어 최신 상태 반영.
- 스켈레톤/에러 바운더리 정상 동작.

---

### Phase 15 — 배포 (Deploying)

**목표:** Vercel 프로덕션 배포.

**Tasks**
- [ ] DB를 운영용 **PostgreSQL**(Supabase/Neon)로 전환: provider 변경, `prisma migrate deploy`.
- [ ] Vercel 프로젝트 연결, 환경변수(세션/GitHub/이미지/DB) 등록.
- [ ] `prisma generate`가 빌드에 포함되도록 `postinstall`/`build` 스크립트 확인.
- [ ] 프로덕션 스모크 테스트(가입→상품등록→채팅).
- [ ] README에 실행/배포 방법 문서화.

**Acceptance Criteria**
- 배포 URL에서 핵심 플로우(가입/로그인/상품/채팅) 정상 동작.

---

## 6. 비기능 요구사항 (NFR)
- **성능**: 첫 로드 LCP < 2.5s(모바일), 이미지 최적화 적용.
- **접근성**: 폼 label 연결, 버튼 대비, 키보드 포커스.
- **보안**: 비번 해시(bcrypt), 세션 쿠키 `httpOnly`, 서버단 소유권 검증(수정/삭제/채팅), 입력 Zod 검증.
- **에러 처리**: 모든 라우트 `error.tsx`, 서버 액션 try/catch + 사용자 메시지.
- **코드 품질**: ESLint/Prettier 통과, 컴포넌트 재사용, 서버/클라 경계 명확.

---

## 7. 환경변수 목록 (.env.example)
```
DATABASE_URL=
COOKIE_PASSWORD=            # iron-session, 32자 이상
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_HASH=
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

---

## 8. 진행 체크리스트 (요약)
- [ ] Phase 0 셋업
- [ ] Phase 1 Tailwind UI
- [ ] Phase 2 DB
- [ ] Phase 3 폼/Zod
- [ ] Phase 4 세션 로그인
- [ ] Phase 5 SMS 로그인
- [ ] Phase 6 GitHub 로그인
- [ ] Phase 7 미들웨어/권한
- [ ] Phase 8 상품 CRUD
- [ ] Phase 9 검색
- [ ] Phase 10 동네생활
- [ ] Phase 11 프로필
- [ ] Phase 12 채팅
- [ ] Phase 13 이미지
- [ ] Phase 14 캐싱/ISR
- [ ] Phase 15 배포

---

### 부록 A. 참고 출처
- 노마드코더 *캐럿마켓 클론코딩* 공개 강의 페이지 및 커리큘럼 섹션 구성(Next.js 14 · Tailwind · Prisma, 총 148강)을 참고해 Phase를 구성함.
- 본 문서는 강의 자막(전사본)을 복제하지 않고, 공개된 커리큘럼 구조와 표준 Next.js 14 풀스택 설계 관행을 바탕으로 독자적으로 작성한 개발 계획서임.
