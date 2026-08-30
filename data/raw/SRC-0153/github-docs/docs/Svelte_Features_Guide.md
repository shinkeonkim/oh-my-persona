# Svelte 기능 가이드 - Video Serving Platform 구현 사례

## 개요

이 문서는 Video Serving Platform 프로젝트에서 사용된 Svelte의 주요 기능들을 실제 구현 사례와 함께 설명합니다. SvelteKit을 기반으로 한 현대적인 웹 애플리케이션의 핵심 패턴들을 다룹니다.

## 📋 목차

1. [SvelteKit 라우팅](#sveltekit-라우팅)
2. [컴포넌트 시스템](#컴포넌트-시스템)
3. [상태 관리 (Stores)](#상태-관리-stores)
4. [라이프사이클 및 이벤트](#라이프사이클-및-이벤트)
5. [반응형 선언](#반응형-선언)
6. [스타일링](#스타일링)
7. [API 통합](#api-통합)
8. [성능 최적화](#성능-최적화)

---

## SvelteKit 라우팅

### 파일 기반 라우팅

프로젝트의 라우팅 구조:
```
src/routes/
├── +layout.svelte          # 전체 레이아웃
├── +page.svelte            # 홈페이지 (/)
├── login/
│   └── +page.svelte        # 로그인 페이지 (/login)
├── register/
│   └── +page.svelte        # 회원가입 페이지 (/register)
├── upload/
│   └── +page.svelte        # 업로드 페이지 (/upload)
├── my-videos/
│   └── +page.svelte        # 내 비디오 페이지 (/my-videos)
└── video/
    └── [id]/
        └── +page.svelte    # 비디오 상세 페이지 (/video/[id])
```

### 동적 라우팅 구현

**비디오 상세 페이지** (`src/routes/video/[id]/+page.svelte`):
```svelte
<script>
  import { page } from '$app/stores';

  $: videoId = $page.params.id; // URL 파라미터 반응적 접근

  onMount(async () => {
    if (videoId) {
      await videoStore.loadVideo(videoId);
    }
  });
</script>
```

**특징**:
- 파일 기반 자동 라우팅
- 동적 파라미터 `[id]` 지원
- `$page.params`를 통한 URL 파라미터 접근

### 네비게이션

**전체 레이아웃** (`src/routes/+layout.svelte`):
```svelte
<script>
  import { page } from '$app/stores';

  // 현재 페이지 활성화 상태 확인
  $: isActive = (path) => $page.url.pathname === path;
</script>

<nav>
  <a href="/" class:active={isActive('/')}>Home</a>
  <a href="/upload" class:active={isActive('/upload')}>Upload</a>
</nav>
```

---

## 컴포넌트 시스템

### 재사용 가능한 컴포넌트

**VideoGrid 컴포넌트** (`src/components/VideoGrid.svelte`):
```svelte
<script>
  import { createEventDispatcher } from 'svelte';

  // Props 정의
  export let videoList = [];
  export let hasMore = true;
  export let isLoading = false;
  export let showActions = false;

  // 이벤트 디스패처
  const dispatch = createEventDispatcher();

  function handleLoadMore() {
    dispatch('loadMore');
  }

  function handleDelete(video) {
    dispatch('delete', video);
  }
</script>

<!-- 템플릿 -->
<div class="video-grid">
  {#each videoList as video (video.id)}
    <div class="video-card">
      <!-- 비디오 카드 내용 -->
      {#if showActions}
        <button on:click={() => handleDelete(video)}>Delete</button>
      {/if}
    </div>
  {/each}
</div>
```

**사용 예시**:
```svelte
<!-- 홈페이지에서 사용 -->
<VideoGrid
  videoList={$videoList}
  {hasMore}
  isLoading={$isLoading}
  on:loadMore={handleLoadMore}
/>

<!-- 내 비디오 페이지에서 사용 -->
<VideoGrid
  videoList={$myVideos}
  {hasMore}
  isLoading={$isLoading}
  showActions={true}
  on:loadMore={handleLoadMore}
  on:delete={handleDelete}
/>
```

### 컴포넌트 Props와 이벤트

**핵심 특징**:
1. **Props 내보내기**: `export let prop`
2. **이벤트 디스패치**: `createEventDispatcher()`
3. **조건부 렌더링**: `{#if}` 블록
4. **리스트 렌더링**: `{#each}` 블록 + 고유 키

---

## 상태 관리 (Stores)

### Writable Store 패턴

**비디오 상태 관리** (`src/stores/videos.js`):
```javascript
import { writable } from 'svelte/store';

// 기본 스토어
export const videoList = writable([]);
export const isLoading = writable(false);

// 페이지네이션 스토어
export const videoPagination = writable({
  skip: 0,
  limit: 12,
  hasMore: true,
  total: 0
});

// 비즈니스 로직을 포함한 스토어 객체
export const videoStore = {
  async loadVideos(append = false) {
    isLoading.set(true);
    try {
      const pagination = await new Promise(resolve => {
        videoPagination.subscribe(value => resolve(value))();
      });

      const data = await videos.getAll(pagination.skip, pagination.limit);

      if (append) {
        videoList.update(existing => [...existing, ...data]);
      } else {
        videoList.set(data);
      }

      videoPagination.update(p => ({
        ...p,
        skip: p.skip + data.length,
        hasMore: data.length === p.limit
      }));
    } finally {
      isLoading.set(false);
    }
  }
};
```

### 인증 상태 관리

**인증 스토어** (`src/stores/auth.js`):
```javascript
export const user = writable(null);
export const isAuthenticated = writable(false);

export const authStore = {
  async login(username, password) {
    try {
      const response = await auth.login(username, password);
      localStorage.setItem('access_token', response.access_token);

      const userInfo = await auth.getCurrentUser();
      user.set(userInfo);
      isAuthenticated.set(true);

      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const userInfo = await auth.getCurrentUser();
      user.set(userInfo);
      isAuthenticated.set(true);
    } catch (error) {
      localStorage.removeItem('access_token');
    }
  }
};
```

### Store 사용법

**컴포넌트에서 Store 사용**:
```svelte
<script>
  import { videoList, isLoading } from '../stores/videos.js';
  import { isAuthenticated, user } from '../stores/auth.js';

  // $ 접두사로 자동 구독
  $: console.log('현재 비디오 수:', $videoList.length);
  $: console.log('로딩 상태:', $isLoading);
  $: console.log('인증 여부:', $isAuthenticated);
</script>

{#if $isAuthenticated}
  <p>환영합니다, {$user?.username}님!</p>
{/if}

{#if $isLoading}
  <div class="loading">로딩 중...</div>
{:else}
  {#each $videoList as video}
    <div>{video.title}</div>
  {/each}
{/if}
```

---

## 라이프사이클 및 이벤트

### onMount와 라이프사이클

**페이지 초기화 패턴**:
```svelte
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  onMount(() => {
    // 인증 확인
    if (!$isAuthenticated) {
      goto('/login');
      return;
    }

    // 데이터 로드
    videoStore.loadVideos();

    // 정리 함수 반환
    return () => {
      console.log('컴포넌트 정리');
    };
  });
</script>
```

### 이벤트 핸들링

**폼 이벤트 처리** (`src/routes/login/+page.svelte`):
```svelte
<script>
  let username = '';
  let password = '';
  let isSubmitting = false;

  async function handleSubmit() {
    if (isSubmitting) return;

    isSubmitting = true;
    const result = await authStore.login(username, password);

    if (result.success) {
      goto('/');
    } else {
      error = result.error;
    }

    isSubmitting = false;
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <input bind:value={username} disabled={isSubmitting} />
  <input bind:value={password} type="password" disabled={isSubmitting} />
  <button type="submit" disabled={isSubmitting}>
    {isSubmitting ? '로그인 중...' : '로그인'}
  </button>
</form>
```

### 파일 업로드 이벤트

**파일 선택 및 검증**:
```svelte
<script>
  let file = null;
  let uploadProgress = 0;

  function handleFileChange(event) {
    const selectedFile = event.target.files[0];

    if (selectedFile) {
      // 파일 타입 검증
      if (!selectedFile.type.startsWith('video/')) {
        error = 'Please select a valid video file';
        return;
      }

      // 크기 검증
      if (selectedFile.size > 1024 * 1024 * 1024) { // 1GB
        error = 'File size must be less than 1GB';
        return;
      }

      file = selectedFile;
    }
  }

  async function handleUpload() {
    const formData = new FormData();
    formData.append('file', file);

    const result = await videoStore.uploadVideo(formData, (progress) => {
      uploadProgress = progress;
    });
  }
</script>

<input type="file" accept="video/*" on:change={handleFileChange} />

{#if uploadProgress > 0}
  <div class="progress-bar">
    <div class="progress-fill" style="width: {uploadProgress}%"></div>
  </div>
{/if}
```

---

## 반응형 선언

### 반응형 문 ($: 구문)

**동적 계산 및 사이드 이펙트**:
```svelte
<script>
  import { page } from '$app/stores';

  let videoId;
  let hasMore = true;

  // URL 파라미터 추출
  $: videoId = $page.params.id;

  // 페이지네이션 상태 동기화
  $: videoPagination.subscribe(pagination => {
    hasMore = pagination.hasMore;
  });

  // 조건부 실행
  $: if (videoId) {
    console.log('비디오 ID 변경:', videoId);
    videoStore.loadVideo(videoId);
  }

  // 계산된 값
  $: fileSize = file ? (file.size / 1024 / 1024).toFixed(2) + ' MB' : '';

  // 복잡한 반응형 로직
  $: {
    if ($videoList.length === 0 && !$isLoading) {
      console.log('비디오 목록이 비어있습니다.');
    }
  }
</script>

<p>파일 크기: {fileSize}</p>
```

### 조건부 클래스

**동적 스타일링**:
```svelte
<script>
  import { page } from '$app/stores';

  $: isActive = (path) => $page.url.pathname === path;
</script>

<nav>
  <a href="/" class:active={isActive('/')}>Home</a>
  <a href="/upload" class:active={isActive('/upload')}>Upload</a>
</nav>

<style>
  a.active {
    background: #333;
    color: white;
  }
</style>
```

---

## 스타일링

### 스코프된 CSS

**컴포넌트별 독립 스타일**:
```svelte
<!-- VideoGrid.svelte -->
<div class="video-grid">
  <div class="video-card">
    <img src={thumbnail} alt={title} />
  </div>
</div>

<style>
  .video-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 2rem;
  }

  .video-card {
    background: white;
    border-radius: 8px;
    transition: transform 0.2s;
  }

  .video-card:hover {
    transform: translateY(-2px);
  }

  /* 미디어 쿼리 */
  @media (max-width: 768px) {
    .video-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
```

### 글로벌 스타일

**앱 전체 스타일** (`src/app.css`):
```css
/* 전역 변수 */
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
}

/* 유틸리티 클래스 */
.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn:disabled {
  background: var(--secondary-color);
  cursor: not-allowed;
}

/* 반응형 그리드 */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

/* 로딩 애니메이션 */
.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

---

## API 통합

### API 서비스 레이어

**API 클라이언트** (`src/lib/api.js`):
```javascript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
});

// 요청 인터셉터 - 토큰 자동 추가
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 비디오 API
export const videos = {
  async getAll(skip = 0, limit = 100) {
    const response = await api.get(`/videos?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async upload(formData, onProgress = null) {
    const response = await api.post('/videos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress ? (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      } : undefined
    });
    return response.data;
  },

  getThumbnailUrl(filename) {
    return `${API_BASE.replace('/api', '')}/api/thumbnails/${filename}`;
  }
};

// 인증 API
export const auth = {
  async login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/token', formData);
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  }
};
```

### API 상태 관리 통합

**Store와 API 연동**:
```javascript
// stores/videos.js
export const videoStore = {
  async uploadVideo(formData, onProgress = null) {
    isLoading.set(true);
    try {
      const data = await videos.upload(formData, onProgress);

      // 성공 시 로컬 상태 업데이트
      myVideos.update(existing => [data, ...existing]);
      videoList.update(existing => [data, ...existing]);

      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Upload failed'
      };
    } finally {
      isLoading.set(false);
    }
  }
};
```

---

## 성능 최적화

### 무한 스크롤 (Intersection Observer)

**VideoGrid 컴포넌트의 최적화**:
```svelte
<script>
  import { onMount } from 'svelte';

  let container;
  let observer;

  onMount(() => {
    // Intersection Observer 설정
    observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasMore && !isLoading) {
        dispatch('loadMore');
      }
    }, {
      threshold: 0.1,
      rootMargin: '100px' // 100px 전에 미리 로드
    });

    return () => {
      if (observer) observer.disconnect();
    };
  });

  $: if (container && observer && hasMore) {
    const sentinel = container.querySelector('.scroll-sentinel');
    if (sentinel) {
      observer.observe(sentinel);
    }
  }
</script>

<div bind:this={container}>
  <!-- 비디오 리스트 -->

  {#if hasMore}
    <div class="scroll-sentinel">
      {#if isLoading}
        <div class="loading">Loading more videos...</div>
      {/if}
    </div>
  {/if}
</div>
```

### 이미지 지연 로딩

**썸네일 최적화**:
```svelte
<img
  src={videos.getThumbnailUrl(video.thumbnail_path)}
  alt={video.title}
  loading="lazy"  <!-- 브라우저 네이티브 지연 로딩 -->
/>
```

### 조건부 렌더링 최적화

**효율적인 조건부 렌더링**:
```svelte
<!-- 좋은 예: 각 항목에 고유 키 제공 -->
{#each videoList as video (video.id)}
  <VideoCard {video} />
{/each}

<!-- 조건부 로딩 최적화 -->
{#if $videoList.length === 0 && !$isLoading}
  <EmptyState />
{:else}
  <VideoGrid videoList={$videoList} />
{/if}
```

---

## 실제 사용 패턴 정리

### 1. 페이지 구성 패턴

```svelte
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated } from '../stores/auth.js';

  // 페이지별 상태
  let isLoading = false;
  let error = '';

  // 인증 체크
  onMount(() => {
    if (!$isAuthenticated) {
      goto('/login');
    }
  });
</script>

<svelte:head>
  <title>페이지 제목</title>
</svelte:head>

<!-- 페이지 내용 -->
```

### 2. 폼 처리 패턴

```svelte
<script>
  let formData = { name: '', email: '' };
  let isSubmitting = false;
  let errors = {};

  async function handleSubmit() {
    errors = {};
    isSubmitting = true;

    try {
      // 검증
      if (!formData.name) errors.name = 'Required';
      if (Object.keys(errors).length > 0) return;

      // API 호출
      await submitForm(formData);
      goto('/success');
    } catch (error) {
      errors.general = error.message;
    } finally {
      isSubmitting = false;
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <input bind:value={formData.name} class:error={errors.name} />
  {#if errors.name}<span class="error">{errors.name}</span>{/if}

  <button type="submit" disabled={isSubmitting}>
    {isSubmitting ? 'Processing...' : 'Submit'}
  </button>
</form>
```

### 3. 데이터 페칭 패턴

```svelte
<script>
  import { onMount } from 'svelte';

  let data = [];
  let loading = false;
  let error = null;

  async function loadData() {
    loading = true;
    error = null;

    try {
      data = await api.getData();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  onMount(loadData);
</script>

{#if loading}
  <div class="loading">Loading...</div>
{:else if error}
  <div class="error">{error}</div>
{:else}
  {#each data as item}
    <div>{item.name}</div>
  {/each}
{/if}
```

---

## 결론

Video Serving Platform 프로젝트에서 사용된 Svelte 기능들을 통해 다음과 같은 이점을 얻었습니다:

### 🎯 핵심 장점

1. **직관적인 문법**: JavaScript와 HTML의 자연스러운 결합
2. **반응형 시스템**: `$:` 구문으로 간단한 반응형 로직
3. **효율적인 상태 관리**: Stores를 통한 전역 상태 관리
4. **성능 최적화**: 컴파일 타임 최적화와 효율적인 DOM 업데이트
5. **개발자 경험**: 적은 보일러플레이트와 명확한 구조

### 🚀 실제 구현된 기능들

- **인증 시스템**: 로그인/로그아웃, 보호된 라우트
- **파일 업로드**: 진행률 표시, 검증, 에러 처리
- **무한 스크롤**: 성능 최적화된 페이지네이션
- **반응형 디자인**: 모바일 친화적 UI
- **실시간 업데이트**: 스토어 기반 상태 동기화

이러한 Svelte의 특성들로 인해 복잡한 비디오 플랫폼을 효율적이고 유지보수 가능한 방식으로 구현할 수 있었습니다.