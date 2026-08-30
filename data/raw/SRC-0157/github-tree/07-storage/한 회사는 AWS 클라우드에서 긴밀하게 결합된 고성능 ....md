## Question

한 회사는 AWS 클라우드에서 긴밀하게 결합된 고성능 컴퓨팅(HPC) 환경을 설계하고 있습니다. 회사는 네트워킹 및 스토리지를 위해 HPC 환경을 최적화하는 기능을 포함해야 합니다.
이러한 요구 사항을 충족하는 솔루션 조합은 무엇입니까? (2개를 선택하세요.)

- [ ] A. AWS Global Accelerator에서 액셀러레이터를 생성합니다. 가속기에 대한 사용자 지정 라우팅을 구성합니다.
- [ ] B. Lustre 파일 시스템용 Amazon FSx를 생성합니다. 스크래치 스토리지로 파일 시스템을 구성합니다.
- [ ] C. Amazon CloudFront 배포판을 생성합니다. 뷰어 프로토콜 정책을 HTTP 및 HTTPS로 구성합니다.
- [ ] D. Amazon EC2 인스턴스를 시작합니다. EFA(Elastic Fabric Adapter)를 인스턴스에 연결합니다.
- [ ] E. 환경을 관리하기 위해 AWS Elastic Beanstalk 배포를 생성합니다.

## Answer

정답: B, D

## Explanation

B(FSx for Lustre 스크래치 파일 시스템)와 D(EFA가 연결된 EC2 인스턴스)가 정답입니다. FSx for Lustre는 HPC에 최적화된 고성능 병렬 파일 시스템으로, 스크래치 파일 시스템은 최대 200GB/s의 처리량과 밀리초 미만의 지연 시간을 제공합니다. EFA(Elastic Fabric Adapter)는 EC2 인스턴스 간 OS-bypass 통신을 지원하여 MPI(Message Passing Interface) 기반의 긴밀하게 결합된 HPC 애플리케이션에 최적의 네트워크 성능을 제공합니다.

오답 분석

A: AWS Global Accelerator는 글로벌 사용자에게 가장 가까운 AWS 엣지 로케이션을 통해 트래픽을 라우팅하는 서비스이며, HPC 클러스터 내 인스턴스 간 저지연 네트워킹과는 관련이 없습니다.

C: Amazon CloudFront는 정적/동적 웹 콘텐츠를 전 세계 엣지 로케이션에서 캐싱하여 배포하는 CDN(Content Delivery Network) 서비스입니다. HPC 환경의 스토리지나 네트워킹 최적화와는 전혀 관련이 없습니다.

E: AWS Elastic Beanstalk는 웹 애플리케이션의 배포와 관리를 자동화하는 PaaS(Platform as a Service)이며, HPC 환경의 스토리지나 네트워킹 최적화에 적합하지 않습니다.

