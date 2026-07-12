# 피치(Peach) — 개발 계획서 / PRD

> **배우고 · 모이고 · 부탁하는 동네 재능 플랫폼.**
> 강의/재능을 파는 **오퍼**, 스터디·소모임(그룹 채팅 + 약속), 숨고식 **역방향 매칭**(의뢰→견적)을 결합한 풀스택 웹앱.
> 노마드코더 *캐럿마켓 클론코딩* 커리큘럼(Next.js 14 · Tailwind · Prisma)의 **뼈대(인증·리스팅·채팅·커뮤니티·프로필·이미지·ISR·배포)** 를 재사용하되, 콘텐츠는 "중고거래"가 아니라 "재능/스터디/서비스 매칭"으로 전환.
> Claude Code가 순차 실행할 수 있도록 최대한 세분화함.

---

## 0. 이 문서를 읽는 Claude Code에게 (실행 지침)

- **한 번에 한 Phase씩**, `Phase 0 → Phase 18` 순서로 진행. Phase 간 의존성이 있다.
- 각 Phase는 **작업 체크리스트(Tasks)** 와 **완료 기준(Acceptance)** 을 가진다. 완료 기준을 모두 만족해야 다음으로.
- Phase 종료 시 **커밋**(`feat(phaseN): ...`).
- UI는 **모바일 우선**(`max-w-screen-sm` 중앙 정렬).
- 타입 엄격(`strict: true`), 서버/클라이언트 경계 명확, 소유권/권한은 **서버단에서** 검증.
- 외부 서비스 키(이미지/실시간/SMS/OAuth)가 없으면 해당 Phase는 **mock/로컬 대체**로 먼저 구현하고 `// TODO(env):` 주석을 남긴다.
- 브랜드 톤: 복숭아빛 메인 컬러 `#FF8B7B`~`#FF6F61`, 포인트 오렌지, 로고 이모지 🍑. 명세 없는 마이크로카피는 이 톤으로 채운다.

---

## 1. 제품 개요

| 항목 | 내용 |
|---|---|
| 서비스명 | 피치 (Peach) — *가칭, 변경 가능* |
| 한 줄 정의 | 동네에서 배우고, 모이고, 부탁하는 재능·스터디·서비스 매칭 플랫폼 |
| 타깃 | 모바일 웹 사용자 |
| 참고 모델 | 탈잉(강의) + 문토·소모임(스터디) + 숨고(양방향 매칭) |
| 브랜드 톤 | 따뜻함, 복숭아, 이웃, 성장 |

### 1.1 세 개의 축
1. **오퍼(Offer) — 파는 사람이 올린다.** 고수/호스트가 등록: `CLASS`(강의/클래스), `STUDY`(스터디·소모임 모집), `SERVICE`(집수리·청소·심부름 등 생활 재능). 가격 `0` = **재능기부(무료)**.
2. **의뢰(Request) — 사는 사람이 올린다 (숨고식 역방향).** "이런 거 배우고 싶어요 / 해주세요"를 올리면, 고수들이 **제안(Proposal, 견적+메시지)** 을 보낸다. 의뢰자가 제안을 수락하면 채팅으로 연결.
3. **소모임(Group) — 함께 모인다.** `STUDY` 오퍼에 참여 신청→수락된 멤버가 **그룹**을 이루고, **그룹 채팅** + **약속(Meetup: 날짜·장소·참석 투표)** 으로 운영.

### 1.2 핵심 사용자 스토리
- U1. 방문자는 전화/이메일/GitHub로 가입·로그인한다.
- U2. **호스트**는 강의·스터디·서비스 오퍼를 사진과 함께 등록한다(가격 또는 무료).
- U3. **탐색자**는 카테고리/검색으로 오퍼를 찾고, 찜하고, 상세에서 신청하거나 1:1 채팅한다.
- U4. **의뢰자**는 원하는 걸 의뢰로 올리고, 들어온 견적(제안)들을 비교해 수락한다.
- U5. **고수**는 의뢰 목록을 보고 견적(제안)을 보낸다.
- U6. 스터디 참여자들은 **그룹 채팅**에서 대화하고 **약속(오프라인 모임)** 일정을 잡고 참석 여부를 투표한다.
- U7. 이용 후 서로 **후기·평점**을 남긴다.
- U8. 사용자는 **프로필**에서 내가 연 오퍼 / 참여한 스터디 / 올린 의뢰 / 받은·보낸 제안 / 찜 / 후기를 관리한다.

---

## 2. 기술 스택

| 레이어 | 선택 | 비고 |
|---|---|---|
| 프레임워크 | **Next.js 14 (App Router)** | Server Components + Server Actions |
| 언어 | **TypeScript** (strict) | |
| 스타일 | **Tailwind CSS** + `@tailwindcss/forms` | |
| ORM | **Prisma** | |
| DB | 개발 **SQLite** → 운영 **PostgreSQL**(Supabase/Neon) | |
| 세션/인증 | **iron-session** 쿠키, `bcrypt` 해시 | |
| 검증 | **Zod** + Server Action + `useActionState` | |
| 이미지 | **Cloudflare Images**(direct upload) / 대체 Supabase Storage | |
| 실시간 | **Supabase Realtime**(1:1 + 그룹 채팅) / 대체 Pusher | |
| 날짜/일정 | `date-fns`, 전화 검증 `libphonenumber-js` | |
| 배포 | **Vercel** | |
| 패키지 | **npm** | |

---

## 3. 최종 라우트 구조 (목표)

```
app/
  (auth)/
    create-account/page.tsx
    login/page.tsx
    sms/page.tsx
    github/{start,complete}/route.ts
  (tabs)/
    (home)/page.tsx              # 오퍼 홈(피드) + 카테고리
    requests/page.tsx           # 의뢰 보드(숨고식)
    groups/page.tsx             # 내 소모임(스터디) 목록
    chat/page.tsx               # 채팅방 목록(1:1+그룹)
    profile/page.tsx            # 나의 피치
    layout.tsx                  # 하단 탭바
  offers/
    add/page.tsx                # 오퍼 등록(kind 선택)
    [id]/page.tsx               # 오퍼 상세(+신청/찜/채팅)
    [id]/edit/page.tsx
  requests/
    add/page.tsx                # 의뢰 등록
    [id]/page.tsx               # 의뢰 상세(+제안 목록/제안 보내기)
  groups/
    [id]/page.tsx               # 소모임 홈(멤버/약속/그룹채팅 진입)
    [id]/meetups/add/page.tsx   # 약속 만들기
  chats/[id]/page.tsx           # 채팅방(1:1 or 그룹)
  posts/                        # 커뮤니티/후기 게시판
    add/page.tsx
    [id]/page.tsx
  search/page.tsx
  users/[id]/page.tsx           # 공개 고수 프로필(평점/후기)
lib/{db.ts,session.ts,utils.ts,realtime.ts}
components/...
prisma/schema.prisma
middleware.ts
```

---

## 4. 데이터 모델 (Prisma 최종 목표)

> Phase마다 **필요한 모델만 점진적으로** 추가·마이그레이션한다. 아래는 최종 형태.

```prisma
model User {
  id         Int      @id @default(autoincrement())
  username   String   @unique
  email      String?  @unique
  password   String?
  phone      String?  @unique
  github_id  String?  @unique
  avatar     String?
  bio        String?
  isHost     Boolean  @default(false)   // 고수/호스트 활동 표시(선택)
  created_at DateTime @default(now())
  updated_at DateTime @updatedAt

  tokens        SMSToken[]
  offers        Offer[]
  requests      Request[]
  proposals     Proposal[]
  enrollments   Enrollment[]
  offerLikes    OfferLike[]
  posts         Post[]
  comments      Comment[]
  postLikes     PostLike[]
  messages      Message[]
  chatRooms     ChatRoom[]     @relation("ChatRoomUsers")
  groupsOwned   Group[]        @relation("GroupOwner")
  groupMembers  GroupMember[]
  meetupRSVPs   MeetupRSVP[]
  reviewsWritten Review[]      @relation("ReviewAuthor")
  reviewsGot     Review[]      @relation("ReviewTarget")
}

model SMSToken {
  id     Int    @id @default(autoincrement())
  token  String @unique
  user   User   @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId Int
  created_at DateTime @default(now())
}

model Category {
  id     Int     @id @default(autoincrement())
  name   String  @unique          // 코딩/바이브코딩, 영어, 디자인, 운동, 독서, 집수리, 청소, 심부름 ...
  icon   String?
  offers Offer[]
  requests Request[]
}

enum OfferKind { CLASS STUDY SERVICE }

model Offer {
  id          Int       @id @default(autoincrement())
  kind        OfferKind
  title       String
  description String
  price       Int       @default(0)  // 0 = 재능기부(무료)
  isDonation  Boolean   @default(false)
  photo       String?
  region      String?
  // STUDY/CLASS 전용(선택)
  capacity    Int?
  startsAt    DateTime?
  category    Category? @relation(fields: [categoryId], references: [id])
  categoryId  Int?
  host        User      @relation(fields: [hostId], references: [id], onDelete: Cascade)
  hostId      Int
  created_at  DateTime  @default(now())
  updated_at  DateTime  @updatedAt

  enrollments Enrollment[]
  likes       OfferLike[]
  group       Group?          // STUDY가 성사되면 생성되는 소모임
  reviews     Review[]
}

model OfferLike {
  offer   Offer @relation(fields: [offerId], references: [id], onDelete: Cascade)
  offerId Int
  user    User  @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId  Int
  created_at DateTime @default(now())
  @@id([offerId, userId])
}

enum EnrollmentStatus { APPLIED ACCEPTED REJECTED CANCELED }

model Enrollment {
  id      Int    @id @default(autoincrement())
  offer   Offer  @relation(fields: [offerId], references: [id], onDelete: Cascade)
  offerId Int
  user    User   @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId  Int
  status  EnrollmentStatus @default(APPLIED)
  message String?
  created_at DateTime @default(now())
  @@unique([offerId, userId])
}

// ===== 숨고식 역방향 매칭 =====
model Request {
  id          Int      @id @default(autoincrement())
  title       String
  description String
  budget      Int?
  region      String?
  desiredAt   DateTime?
  category    Category? @relation(fields: [categoryId], references: [id])
  categoryId  Int?
  author      User     @relation(fields: [authorId], references: [id], onDelete: Cascade)
  authorId    Int
  isClosed    Boolean  @default(false)
  created_at  DateTime @default(now())
  updated_at  DateTime @updatedAt
  proposals   Proposal[]
}

enum ProposalStatus { PENDING ACCEPTED REJECTED }

model Proposal {
  id        Int    @id @default(autoincrement())
  request   Request @relation(fields: [requestId], references: [id], onDelete: Cascade)
  requestId Int
  provider  User   @relation(fields: [providerId], references: [id], onDelete: Cascade)
  providerId Int
  price     Int?
  message   String
  status    ProposalStatus @default(PENDING)
  created_at DateTime @default(now())
  @@unique([requestId, providerId])
}

// ===== 소모임 =====
model Group {
  id       String   @id @default(cuid())
  name     String
  offer    Offer    @relation(fields: [offerId], references: [id], onDelete: Cascade)
  offerId  Int      @unique
  owner    User     @relation("GroupOwner", fields: [ownerId], references: [id])
  ownerId  Int
  members  GroupMember[]
  meetups  Meetup[]
  chatRoom ChatRoom? @relation(fields: [chatRoomId], references: [id])
  chatRoomId String? @unique
  created_at DateTime @default(now())
}

model GroupMember {
  group   Group @relation(fields: [groupId], references: [id], onDelete: Cascade)
  groupId String
  user    User  @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId  Int
  role    String @default("member") // owner|member
  joined_at DateTime @default(now())
  @@id([groupId, userId])
}

model Meetup {
  id       Int      @id @default(autoincrement())
  group    Group    @relation(fields: [groupId], references: [id], onDelete: Cascade)
  groupId  String
  title    String
  place    String?
  startsAt DateTime
  created_at DateTime @default(now())
  rsvps    MeetupRSVP[]
}

enum RSVPStatus { GOING MAYBE NO }

model MeetupRSVP {
  meetup   Meetup @relation(fields: [meetupId], references: [id], onDelete: Cascade)
  meetupId Int
  user     User   @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId   Int
  status   RSVPStatus @default(GOING)
  @@id([meetupId, userId])
}

// ===== 채팅(1:1 + 그룹) =====
model ChatRoom {
  id       String    @id @default(cuid())
  isGroup  Boolean   @default(false)
  users    User[]    @relation("ChatRoomUsers")
  messages Message[]
  group    Group?
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
}

// ===== 커뮤니티/후기 =====
model Post {
  id    Int    @id @default(autoincrement())
  title String
  description String?
  views Int    @default(0)
  user  User   @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId Int
  created_at DateTime @default(now())
  comments Comment[]
  likes    PostLike[]
}
model Comment {
  id      Int    @id @default(autoincrement())
  payload String
  user    User   @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId  Int
  post    Post   @relation(fields: [postId], references: [id], onDelete: Cascade)
  postId  Int
  created_at DateTime @default(now())
}
model PostLike {
  post   Post @relation(fields: [postId], references: [id], onDelete: Cascade)
  postId Int
  user   User @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId Int
  @@id([postId, userId])
}

model Review {
  id       Int    @id @default(autoincrement())
  rating   Int    // 1~5
  payload  String?
  offer    Offer? @relation(fields: [offerId], references: [id], onDelete: SetNull)
  offerId  Int?
  author   User   @relation("ReviewAuthor", fields: [authorId], references: [id])
  authorId Int
  target   User   @relation("ReviewTarget", fields: [targetId], references: [id])
  targetId Int
  created_at DateTime @default(now())
}
```

---

## 5. 개발 Phase (세분화)

### Phase 0 — 프로젝트 셋업
**Tasks**
- [ ] `create-next-app`(TS·ESLint·Tailwind·App Router·alias `@/*`)로 `peach-market/` 하위 스캐폴드.
- [ ] 보일러플레이트 정리, `globals.css` Tailwind 지시문만, 모바일 컨테이너 레이아웃.
- [ ] `prettier` + `prettier-plugin-tailwindcss`, `.env`/`.env.example`/`.gitignore`.
- [ ] `npm run dev`/`build` 정상.

**Acceptance:** dev/build 무에러, strict 통과.

---

### Phase 1 — 디자인/Tailwind 워밍업
**Tasks**
- [ ] `@tailwindcss/forms`, `heroicons` 설치.
- [ ] 공통 컴포넌트: `input.tsx`, `button.tsx`(loading), `social-login.tsx`.
- [ ] 정적 화면: `/login`, `/create-account`, 오퍼 홈 피드(카드: 썸네일·제목·가격 or "무료·재능기부" 뱃지·카테고리·지역).
- [ ] 하단 탭바 `(tabs)/layout.tsx`: 홈 / 의뢰 / 소모임 / 채팅 / 프로필.
- [ ] 플로팅 "＋" (오퍼/의뢰 등록 진입).

**Acceptance:** 로그인·회원가입·홈·탭바가 모바일 폭에서 렌더.

---

### Phase 2 — DB 셋업
**Tasks**
- [ ] Prisma 설치·init(sqlite), `lib/db.ts` 싱글턴.
- [ ] 최소 모델 `User`, `Category`, `Offer`(+`OfferKind`) 정의.
- [ ] `prisma migrate dev --name init`.
- [ ] 시드 스크립트로 카테고리 기본값 주입(코딩·바이브코딩/영어/디자인/운동/독서/집수리/청소/심부름 등).

**Acceptance:** 마이그레이션·시드 성공, `db.category.findMany()` 반환.

---

### Phase 3 — 폼 & 검증(Zod + Server Action)
**Tasks**
- [ ] `zod` 설치. 회원가입 Server Action + Zod(한글 에러, username 3~10, password 규칙, confirm refine, 중복검사).
- [ ] `useActionState`로 필드별 에러 표시. `bcrypt` 해시 저장.

**Acceptance:** 잘못된 입력 필드 에러·미저장, 정상 입력 유저 생성.

---

### Phase 4 — 인증: 세션 로그인
**Tasks**
- [ ] `iron-session`, `lib/session.ts`(`getSession`, 쿠키 `peach`).
- [ ] 가입 성공 시 세션 저장→`/profile`. `/login` 액션(bcrypt.compare). 로그아웃(`destroy`).

**Acceptance:** 세션 유지/소멸 정상.

---

### Phase 5 — SMS(전화번호) 로그인
**Tasks**
- [ ] `/sms` 2단계 폼(전화→토큰), `libphonenumber-js` KR 검증.
- [ ] 6자리 토큰 발급/저장(재발급 시 기존 삭제), 외부 SMS 없으면 콘솔 출력 대체(`TODO(env)`).
- [ ] 토큰 검증→세션.

**Acceptance:** 유효번호 토큰 발급, 오답 거부, 정답 로그인.

---

### Phase 6 — GitHub OAuth
**Tasks**
- [ ] `/github/start` authorize 리다이렉트, `/github/complete` 콜백(code→token→user/emails).
- [ ] `github_id` 매칭/신규 생성(avatar 저장)→세션. `social-login` 연결.

**Acceptance:** 최초 자동가입/재로그인 동일유저 매칭.

---

### Phase 7 — 미들웨어/권한
**Tasks**
- [ ] `middleware.ts` public 화이트리스트(`/`, auth 경로), 세션 쿠키 분기, matcher 정적 제외.

**Acceptance:** 비로그인→보호경로 차단, 로그인→auth경로 차단.

---

### Phase 8 — 오퍼 CRUD (핵심 ①)
**Tasks**
- [ ] `Enrollment`, `OfferLike` 모델 추가·마이그레이션.
- [ ] **등록** `/offers/add`: `kind`(CLASS/STUDY/SERVICE) 선택 → 조건부 필드(가격 or 무료 토글, capacity·startsAt는 CLASS/STUDY, region, category, 이미지 미리보기). Server Action 생성.
- [ ] **홈 피드** `(home)/page.tsx`: 최신순 목록 + `kind`/카테고리 필터 탭. 무료면 "재능기부" 뱃지.
- [ ] **상세** `/offers/[id]`: 호스트 정보(평점), 설명, 가격/무료, (CLASS/STUDY) 정원·시작일·잔여석. 버튼: 본인=수정/삭제, 타인=신청하기 + 1:1 채팅.
- [ ] **수정/삭제** 본인 검증. **찜** 토글(optimistic).
- [ ] **이미지 업로드**: Cloudflare direct-upload route(키 없으면 `public/uploads` 로컬 대체 `TODO(env)`).

**Acceptance:** 3종 kind 등록·조회·수정·삭제, 소유권 서버 검증, 찜 즉시 반영, 이미지 표시.

---

### Phase 9 — 신청 & 정원 관리 (Enrollment)
**Tasks**
- [ ] 상세에서 "신청하기"→`Enrollment(APPLIED)` 생성(중복 방지, 메시지 옵션).
- [ ] 호스트용 신청자 목록 UI: 수락/거절(`ACCEPTED/REJECTED`), 잔여석 = capacity − ACCEPTED 수.
- [ ] 정원 초과/마감 처리, 신청 취소.

**Acceptance:** 신청→호스트 수락/거절→잔여석 반영, 정원 초과 차단.

---

### Phase 10 — 검색 & 카테고리 필터
**Tasks**
- [ ] `/search`: 오퍼 title/description + 카테고리/kind/지역 필터, empty state.
- [ ] 홈 카테고리 칩 → 필터 연동.

**Acceptance:** 키워드/필터 조합 정확.

---

### Phase 11 — 숨고식 의뢰 & 제안 (핵심 ③)
**Tasks**
- [ ] `Request`, `Proposal` 모델 추가·마이그레이션.
- [ ] **의뢰 등록** `/requests/add`: title/description/budget/region/desiredAt/category. (사는 사람 관점)
- [ ] **의뢰 보드** `(tabs)/requests`: 최신순 + 카테고리 필터, 제안 수 표시.
- [ ] **의뢰 상세** `/requests/[id]`: 본인이면 들어온 **제안 목록**(가격·메시지·고수 평점) + 수락. 타인(고수)이면 **제안 보내기** 폼.
- [ ] 제안 수락 시: 다른 제안 참고 처리, 의뢰자↔고수 **1:1 채팅방 자동 생성**, `Request.isClosed=true`.

**Acceptance:** 의뢰 등록→고수 제안→의뢰자 수락→채팅 연결, 본인 의뢰엔 제안 불가.

---

### Phase 12 — 1:1 실시간 채팅 (핵심 채팅)
**Tasks**
- [ ] `ChatRoom`(isGroup), `Message` 모델 마이그레이션.
- [ ] 오퍼 상세/제안 수락에서 1:1 방 생성(기존 방 재사용).
- [ ] `(tabs)/chat` 목록(마지막 메시지·상대 아바타), `/chats/[id]` 말풍선 좌우 구분.
- [ ] **Supabase Realtime** 구독으로 실시간 수신(키 없으면 폴링/mock `TODO(env)`), 전송 시 DB저장+optimistic+broadcast.
- [ ] 참여자만 입장(서버 검증).

**Acceptance:** 두 계정 실시간 송수신, 무관 유저 차단.

---

### Phase 13 — 소모임(그룹) & 그룹 채팅 (핵심 ②)
**Tasks**
- [ ] `Group`, `GroupMember` 모델 마이그레이션.
- [ ] STUDY 오퍼의 신청이 **ACCEPTED**되면 그룹 자동 생성/합류(owner=호스트), 그룹 전용 `ChatRoom(isGroup=true)` 연결.
- [ ] `(tabs)/groups`: 내가 속한 소모임 목록. `/groups/[id]`: 멤버 목록·소개·그룹채팅 진입.
- [ ] 그룹 채팅: 발신자 이름/아바타 표시(1:1과 렌더 분기).

**Acceptance:** 스터디 수락→그룹·그룹채팅 생성, 멤버 다자 대화.

---

### Phase 14 — 약속(Meetup) & 참석 투표
**Tasks**
- [ ] `Meetup`, `MeetupRSVP` 모델 마이그레이션.
- [ ] `/groups/[id]/meetups/add`: title/place/startsAt(멤버만).
- [ ] 그룹 홈에 다가오는 약속 리스트, **참석/미정/불참** 투표(RSVP) + 인원 집계.
- [ ] (선택) 지난 약속 아카이브.

**Acceptance:** 약속 생성→멤버 RSVP→집계 반영.

---

### Phase 15 — 후기 & 평점 (Review)
**Tasks**
- [ ] `Review` 모델 마이그레이션.
- [ ] 완료된 오퍼/서비스에 대해 작성자→호스트(target) 별점(1~5)+글.
- [ ] `users/[id]` 공개 프로필: 평균 평점·후기 목록·연 오퍼.
- [ ] 오퍼 상세/의뢰 제안에 호스트 평점 노출.

**Acceptance:** 후기 작성→공개 프로필·평균 평점 반영, 중복/자기평가 방지.

---

### Phase 16 — 커뮤니티 게시판 (동네생활 대체)
**Tasks**
- [ ] `Post`, `Comment`, `PostLike` 마이그레이션.
- [ ] 자유/후기/질문 게시판: 목록·작성·상세(조회수)·좋아요(optimistic)·댓글.

**Acceptance:** 글·댓글·좋아요 CRUD, 낙관적 업데이트.

---

### Phase 17 — 이미지 최적화 & 캐싱/ISR
**Tasks**
- [ ] `next.config` `images.remotePatterns`, 카드=썸네일/상세=원본 variants.
- [ ] `unstable_cache`/`revalidateTag`/`revalidatePath`로 오퍼·의뢰·프로필 캐싱·무효화.
- [ ] `loading.tsx`/`error.tsx`/Suspense 스켈레톤.

**Acceptance:** 이미지 최적 로드, 데이터 변경 재검증 반영.

---

### Phase 18 — 배포
**Tasks**
- [ ] DB PostgreSQL 전환(`migrate deploy`), Vercel 연결·환경변수 등록.
- [ ] `postinstall: prisma generate`, 스모크 테스트(가입→오퍼→신청/의뢰→채팅→약속).
- [ ] README 작성.

**Acceptance:** 배포 URL에서 3축(오퍼/의뢰/소모임) 핵심 플로우 동작.

---

## 6. MVP 경계 (먼저 vs 나중)
- **MVP(먼저):** Phase 0~12 — 인증 + 오퍼 CRUD/신청 + 검색 + 의뢰·제안 + 1:1 채팅.
- **V1.1:** Phase 13~15 — 소모임/그룹채팅 + 약속 + 후기.
- **V1.2:** Phase 16~18 — 커뮤니티 + 최적화 + 배포.
- **결제/정산은 범위 밖**(초기엔 무료/재능기부·현장결제 가정). 필요 시 후속 Phase로 PG 연동.

## 7. 비기능 요구사항
- 성능(모바일 LCP<2.5s, 이미지 최적화), 접근성(label·대비·포커스), 보안(bcrypt·httpOnly 세션·서버단 소유권/멤버십 검증·Zod), 에러 처리(라우트별 `error.tsx`, 액션 try/catch), 코드품질(ESLint/Prettier, 서버·클라 경계).

## 8. 환경변수 (.env.example)
```
DATABASE_URL=
COOKIE_PASSWORD=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_HASH=
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

## 9. 진행 체크리스트
- [ ] P0 셋업 · [ ] P1 UI · [ ] P2 DB · [ ] P3 폼/Zod · [ ] P4 세션 · [ ] P5 SMS · [ ] P6 GitHub · [ ] P7 미들웨어
- [ ] P8 오퍼CRUD · [ ] P9 신청/정원 · [ ] P10 검색 · [ ] P11 의뢰·제안 · [ ] P12 1:1채팅
- [ ] P13 소모임·그룹채팅 · [ ] P14 약속·RSVP · [ ] P15 후기·평점 · [ ] P16 커뮤니티 · [ ] P17 이미지·ISR · [ ] P18 배포

---

### 부록. 설계 메모
- **왜 Offer/Request 2모델인가:** 숨고식 양방향(파는 사람↔사는 사람)을 한 테이블에 `mode`로 욱여넣으면 필드가 서로 어긋난다(오퍼=정원/시작일, 의뢰=예산/희망일). 분리가 쿼리·UI 모두 단순.
- **소모임 = STUDY 오퍼의 후속 상태:** 별도 "그룹 생성" UX 없이, 스터디 신청 수락이 곧 그룹 합류가 되어 흐름이 자연스럽다.
- **채팅 1:1/그룹 통합:** `ChatRoom.isGroup` 하나로 두 케이스를 같은 인프라(Realtime)로 처리.
- 본 문서는 강의 자막을 복제하지 않고, 공개 커리큘럼 구조 + 표준 Next.js 14 풀스택 설계로 독자 작성함.
