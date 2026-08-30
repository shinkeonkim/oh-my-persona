# Dice Art Visualizer 🎲

Dice Art Visualizer는 사용자가 특정 이미지 파일을 업로드하면, 해당 이미지를 분석하여 1부터 6까지 점이 찍힌 주사위 눈금으로 변환하여 **새로운 주사위 모자이크 아트**를 생성하고 이를 **2D/3D 웹 환경에서 시각화**하는 고성능 웹 서비스 구현 프로젝트입니다. 

라이브 링크: [http://dice-art.코드.kr/](http://dice-art.xn--hy1by51c.kr/)

## 기술 스택 및 최적화 기법
- **React (Vite) / TypeScript**: 빠르고 안정적인 서비스 구동 및 개발
- **Web Worker / Offscreen Canvas**: 초대형 이미지를 처리할 때도 메인 스레드(UI) 멈춤 현상이 발생하지 않도록 비동기 파이프라인 구성
- **Floyd-Steinberg 디더링 및 Auto-Contrast**: 오직 6개의 명암(주사위 눈금)만으로 자연스러운 이미지를 매핑하기 위해 오차 확산 알고리즘과 명암비 강제 확장을 도입하여 선명한 결과물을 만들어냅니다.
- **Three.js / React Three Fiber**: 수십만 개의 3D 주사위를 버벅임 없이 렌더링하기 위해 `InstancedMesh` 기술을 적극 활용했습니다.
- **Tailwind CSS v4**: 빠르고 직관적인 UI 프레임워크 구축.

## 주요 기능
1. **이미지 프로세싱**: PNG, JPG 해상도 자동 리사이즈 및 변환.
2. **해상도 조절**: 주사위의 개수를 실시간으로 조절하여 모자이크 해상도 조정 (Max 200x200 = 40,000개 주사위 지원).
3. **테마(Invert) 모드**: 다크 모드(검정 바탕 흰색 점) 및 라이트 모드(하얀 바탕 검정 점) 전환.
4. **결과물 Export**: 단 한 번의 클릭을 통해 현재 만들어진 주사위 예술을 고해상도 PNG로 다운로드.

## 실행 방법

```bash
# 패키지 설치
npm install

# 서비스 시작 (http://localhost:5174)
npm run dev
```
