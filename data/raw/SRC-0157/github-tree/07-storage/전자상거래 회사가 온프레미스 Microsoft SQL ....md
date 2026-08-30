## Question

전자상거래 회사가 온프레미스 Microsoft SQL Server 데이터베이스를 AWS 클라우드로 마이그레이션할 계획입니다. 이 회사는 데이터베이스를 SQL Server Always On 가용성 그룹으로 마이그레이션해야 합니다. 클라우드 기반 솔루션은 고가용성이어야 합니다.
솔루션 아키텍트는 이러한 요구 사항을 충족하기 위해 무엇을 해야 합니까?

- [ ] A. SQL Server가 있는 Amazon EC2 인스턴스 3개를 3개의 가용성 영역에 배포합니다. Amazon Elastic Block Store (Amazon EBS) 볼륨 하나를 EC2 인스턴스에 연결합니다.
- [ ] B. 데이터베이스를 SQL Server용 Amazon RDS로 마이그레이션합니다. 다중 AZ 배포와 읽기 복제본을 구성합니다.
- [ ] C. SQL Server가 있는 Amazon EC2 인스턴스 3개를 3개의 가용성 영역에 배포합니다. Amazon FSx for Windows File Server를 스토리지 계층으로 사용합니다.
- [ ] D. SQL Server가 있는 Amazon EC2 인스턴스 3개를 3개의 가용성 영역에 배포합니다. Amazon S3를 스토리지 계층으로 사용합니다.

## Answer

정답: C

## Explanation

SQL Server Always On 가용성 그룹은 Windows Server Failover Clustering(WSFC)을 기반으로 하며, 공유 스토리지로 SMB 파일 공유가 필요합니다. 3개의 가용 영역에 EC2 인스턴스를 배포하여 고가용성을 확보하고, Amazon FSx for Windows File Server를 파일 증인(File Share Witness) 및 공유 스토리지로 사용하면 Always On 가용성 그룹을 완전히 지원합니다. FSx는 Multi-AZ 배포로 스토리지 계층의 고가용성도 보장합니다.

오답 분석

A: 단일 EBS 볼륨을 여러 EC2 인스턴스에 공유할 수 없으며(io1/io2 Multi-Attach는 제한적), Always On 가용성 그룹에 필요한 공유 스토리지를 제공하지 못합니다.

B: Amazon RDS for SQL Server는 관리형 서비스로 Multi-AZ를 지원하지만, Always On 가용성 그룹은 EC2 기반 자체 관리형 SQL Server에서만 구성할 수 있습니다.

D: Amazon S3는 객체 스토리지로, SQL Server의 데이터베이스 파일(.mdf, .ldf)을 직접 호스팅하는 블록/파일 스토리지로 사용할 수 없습니다.

