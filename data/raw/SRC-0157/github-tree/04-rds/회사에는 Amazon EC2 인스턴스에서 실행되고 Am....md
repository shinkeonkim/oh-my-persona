## Question

회사에는 Amazon EC2 인스턴스에서 실행되고 Amazon Aurora 데이터베이스를 사용하는 애플리케이션이 있습니다. EC2 인스턴스는 파일에 로컬로 저장된 사용자 이름과 암호를 사용하여 데이터베이스에 연결합니다. 회사는 자격 증명 관리의 운영 오버헤드를 최소화하려고 합니다.
이 목표를 달성하기 위해 솔루션 설계자는 무엇을 해야 합니까?

- [ ] A. AWS Secrets Manager를 사용합니다. 자동 교체를 킵니다.
- [ ] B. AWS Systems Manager Parameter Store를 사용합니다. 자동 교체를 킵니다.
- [ ] C. AWS Key Management Service(AWS KMS) 암호화 키로 암호화된 객체를 저장할 Amazon S3 버킷을 생성합니다. 자격 증명 파일을 S3 버킷으로 마이그레이션합니다. 애플리케이션이 S3 버킷을 가리키도록 합니다.
- [ ] D. 각 EC2 인스턴스에 대해 암호화된 Amazon Elastic Block Store(Amazon EBS) 볼륨을 생성합니다. 새 EBS 볼륨을 각 EC2 인스턴스에 연결합니다. 자격 증명 파일을 새 EBS 볼륨으로 마이그레이션합니다. 애플리케이션이 새 EBS 볼륨을 가리키도록 합니다.

## Answer

정답: A

## Explanation

AWS Secrets Manager를 사용하고 자동 교체를 활성화하면 자격 증명 관리의 운영 오버헤드를 최소화할 수 있습니다. Secrets Manager는 Amazon Aurora 데이터베이스와 네이티브 통합을 제공하며, 자동 교체 기능을 통해 정기적으로 비밀번호를 자동으로 교체합니다. 애플리케이션은 런타임에 Secrets Manager API를 호출하여 최신 자격 증명을 가져오므로 로컬 파일에 자격 증명을 저장할 필요가 없습니다.

오답 분석

B: AWS Systems Manager Parameter Store는 자격 증명을 저장할 수 있지만, 기본적인 자동 교체 기능을 제공하지 않습니다. Parameter Store의 SecureString 파라미터는 자동 교체를 지원하지 않으므로 별도의 Lambda 함수를 구현해야 합니다.

C: S3 버킷에 KMS로 암호화된 자격 증명 파일을 저장하는 방식은 자격 증명 교체 시 파일을 업데이트해야 하므로 운영 오버헤드가 증가합니다. 자동 교체 기능이 없습니다.

D: 각 EC2 인스턴스에 암호화된 EBS 볼륨을 생성하여 자격 증명 파일을 저장하는 방식은 기존 로컬 파일 방식과 크게 다르지 않으며, 각 인스턴스의 자격 증명을 개별적으로 관리해야 하므로 운영 오버헤드가 가장 큽니다.

