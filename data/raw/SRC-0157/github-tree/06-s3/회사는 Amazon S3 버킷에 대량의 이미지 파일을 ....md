## Question

회사는 Amazon S3 버킷에 대량의 이미지 파일을 저장합니다. 이미지는 처음 180일 동안 쉽게 사용할 수 있어야 합니다. 다음 180일 동안 이미지에 자주 액세스하지 않습니다. 360일이 지나면 이미지를 보관해야 하지만 요청 시 즉시 사용할 수 있어야 합니다. 5년 후에는 감사자만 이미지에 액세스할 수 있습니다. 감사자는 12시간 이내에 이미지를 검색할 수 있어야 합니다. 이 과정에서 이미지가 손실될 수 없습니다.
개발자는 처음 180일 동안 S3 Standard 스토리지를 사용합니다. 개발자는 S3 수명 주기 규칙을 구성해야 합니다.
이러한 요구 사항을 가장 비용 효율적으로 충족하는 솔루션은 무엇입니까?

- [ ] A. 180일 후에 객체를 S3 One Zone-Infrequent Access(S3 One Zone-IA)로 전환하고, 360일 후에 S3 Glacier Instant Retrieval로 전환하고, 5년 후에 S3 Glacier Deep Archive로 전환합니다.
- [ ] B. 180일 후에 객체를 S3 One Zone-Infrequent Access(S3 One Zone-IA)로 전환하고, 360일 후에 S3 Glacier Flexible Retrieval로 전환하고, 5년 후에 S3 Glacier Deep Archive로 전환합니다.
- [ ] C. 180일 후에 객체를 S3 Standard-Infrequent Access(S3 Standard-IA)로 전환하고, 360일 후에 S3 Glacier Instant Retrieval로 전환하고, 5년 후에 S3 Glacier Deep Archive로 전환합니다.
- [ ] D. 180일 후에 객체를 S3 Standard-Infrequent Access(S3 Standard-IA)로 전환하고, 360일 후에 S3 Glacier Flexible Retrieval으로, 5년 후에 S3 Glacier Deep Archive로 전환합니다.

## Answer

정답: C

## Explanation

180일 후 S3 Standard-IA로 전환하면 자주 액세스하지 않는 데이터를 저렴하게 저장하면서 즉시 접근이 가능합니다. 360일 후 S3 Glacier Instant Retrieval로 전환하면 아카이브하면서도 즉시 접근 요구 사항을 충족합니다. 5년 후 S3 Glacier Deep Archive로 전환하면 12시간 이내 검색이 가능합니다. 이미지가 손실될 수 없으므로 여러 AZ에 저장하는 Standard-IA를 사용합니다.

오답 분석

A: S3 One Zone-IA는 단일 가용 영역에만 저장하여 '이미지가 손실될 수 없다'는 요구 사항에 적합하지 않습니다.

B: S3 One Zone-IA의 내구성 문제와 함께, S3 Glacier Flexible Retrieval은 즉시 접근이 불가능하여 '요청 시 즉시 사용 가능' 요구 사항을 충족하지 못합니다.

D: S3 Glacier Flexible Retrieval은 360일 후 즉시 접근 요구 사항을 충족하지 못합니다. Glacier Flexible Retrieval의 검색에는 수 분에서 수 시간이 소요됩니다.

