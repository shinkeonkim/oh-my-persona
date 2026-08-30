## Question

한 회사는 Amazon S3를 사용하여 정적 웹 사이트를 호스팅합니다. 회사는 웹페이지에 문의 양식을 추가하려고 합니다. 문의 양식에는 사용자가 이름, 이메일 주소, 전화번호 및 사용자 메시지를 입력할 수 있는 동적 서버측 구성 요소가 있습니다.
회사에서는 매월 사이트 방문 횟수가 100회 미만일 것으로 예상합니다. 문의 양식은 고객이 양식을 작성할 때 이메일로 회사에 알려야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. Amazon Elastic Container Service(Amazon ECS)에서 동적 문의 양식을 호스팅합니다. 타사 이메일 공급자에 연결하려면 Amazon Simple Email Service(Amazon SES)를 설정합니다.
- [ ] B. AWS Lambda 함수에서 문의 양식을 반환하는 Amazon API Gateway 엔드포인트를 생성합니다. Amazon Simple Notification Service(Amazon SNS) 주제에 메시지를 게시하도록 API Gateway에서 또 다른 Lambda 함수를 구성합니다.
- [ ] C. 정적 콘텐츠와 동적 콘텐츠에 AWS Amplify 호스팅을 사용하여 웹 사이트를 호스팅합니다. 서버측 스크립팅을 사용하여 문의 양식을 작성합니다. 메시지를 회사에 전달하도록 Amazon Simple Queue Service(Amazon SQS)를 구성합니다.
- [ ] D. 웹 사이트를 Amazon S3에서 Windows Server를 실행하는 Amazon EC2 인스턴스로 마이그레이션합니다. Windows Server용 인터넷 정보 서비스(IIS)를 사용하여 웹 페이지를 호스팅합니다. 클라이언트측 스크립팅을 사용하여 문의 양식을 작성합니다. 양식을 Amazon WorkMail과 통합합니다.

## Answer

정답: B

## Explanation

API Gateway HTTPS 엔드포인트로 contact form 제출을 수신하고, Lambda 함수에서 폼 데이터를 처리한 후, SNS 토픽을 통해 이메일 알림을 전송합니다. 월 100회 미만의 저빈도 트래픽에서 완전 서버리스 아키텍처는 사용한 만큼만 과금되어 비용이 최소화됩니다. 기존 S3 정적 웹사이트는 그대로 유지하고, contact form의 JavaScript에서 API Gateway 엔드포인트로 AJAX 요청을 보내면 됩니다. SNS는 이메일 구독으로 간편하게 알림을 설정할 수 있습니다.

오답 분석

A: Amazon ECS에서 동적 contact form을 호스팅하면 컨테이너가 상시 실행되어 유휴 비용이 발생합니다. 월 100회 미만의 저빈도 사용에서는 Lambda의 pay-per-request가 훨씬 비용 효율적입니다.

C: AWS Amplify Hosting은 정적 및 동적 콘텐츠를 모두 지원하지만, 옵션 C의 핵심 문제는 Amazon SQS가 메시지 큐 서비스로, 이메일 알림 등의 메시지를 회사에 직접 전달할 수 없다는 점입니다. SQS 큐에서 메시지를 읽고 실제 알림을 전송하는 컨슈머가 여전히 필요하여 불필요한 복잡성이 추가됩니다. 또한 contact form만 개선하면 되는 상황에서 기존 S3 호스팅의 정적 콘텐츠를 Amplify Hosting으로 마이그레이션하는 것은 과도한 변경입니다.

D: Amazon EC2에 Windows Server와 IIS를 배포하면 라이선스 비용, 서버 관리, OS 패칭 등 높은 운영 비용과 오버헤드가 발생합니다. 월 100회 사용에 상시 서버는 극도로 비효율적입니다.

