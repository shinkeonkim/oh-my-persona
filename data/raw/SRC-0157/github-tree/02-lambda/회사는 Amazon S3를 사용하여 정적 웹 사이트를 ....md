## Question

회사는 Amazon S3를 사용하여 정적 웹 사이트를 호스팅합니다. 회사는 웹 페이지에 연락처 양식을 추가하려고 합니다. 연락처 양식에는 사용자가 이름, 이메일 주소, 전화번호 및 사용자 메시지를 입력할 수 있는 동적 서버 측 구성 요소가 있습니다. 회사는 매월 100회 미만의 사이트 방문이 있을 것으로 예상합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. Amazon Elastic Container Service(Amazon ECS)에서 동적 문의 양식 페이지를 호스팅합니다. 타사 이메일 공급자에 연결하도록 Amazon Simple Email Service(Amazon SES)를 설정합니다.
- [ ] B. Amazon Simple Email Service(Amazon SES)를 호출하는 AWS Lambda 백엔드로 Amazon API Gateway 엔드포인트를 생성합니다.
- [ ] C. Amazon Lightsail을 배포하여 정적 웹 페이지를 동적으로 변환합니다. 클라이언트 측 스크립팅을 사용하여 연락처 양식을 작성합니다. 양식을 Amazon WorkMail과 통합합니다.
- [ ] D. t2.micro Amazon EC2 인스턴스를 생성합니다. LAMP(Linux, Apache, MySQL, PHP/Perl/Python) 스택을 배포하여 웹 페이지를 호스팅합니다. 클라이언트 측 스크립팅을 사용하여 연락처 양식을 작성합니다. 양식을 Amazon WorkMail과 통합합니다.

## Answer

정답: B

## Explanation

Amazon API Gateway HTTPS 엔드포인트로 contact form 요청을 수신하고, AWS Lambda 함수에서 폼 데이터를 처리한 후 Amazon SES를 통해 이메일을 전송합니다. 월 100회 미만의 낮은 트래픽에서 완전 서버리스 아키텍처는 pay-per-request 과금으로 가장 비용 효율적입니다. Lambda는 요청이 없을 때 비용이 발생하지 않으며, SES는 저렴한 이메일 전송 비용을 제공합니다. 기존 S3 정적 웹사이트를 변경하지 않고 API 엔드포인트만 추가하면 됩니다.

오답 분석

A: Amazon ECS는 컨테이너 기반 서비스로, 최소 하나의 태스크가 항상 실행되어야 하므로 월 100회 미만의 저빈도 트래픽에서는 유휴 비용이 과도합니다. 서버리스 Lambda 대비 비용 비효율적입니다.

C: Amazon Lightsail로 전환하면 정적 사이트를 동적 서버로 마이그레이션해야 하며, 월 고정 비용이 발생합니다. 기존 S3 정적 호스팅을 유지하면서 contact form만 추가하는 것이 더 간단합니다.

D: EC2 인스턴스에 LAMP 스택을 배포하면 24/7 인스턴스 운영 비용, OS 패칭, 보안 관리 등 높은 운영 오버헤드가 발생합니다. 월 100회 미만 사용에 상시 서버는 극도로 비효율적입니다.

