## Question

솔루션 설계자는 Amazon S3 버킷에 업로드된 모든 객체가 암호화되도록 하려면 어떻게 해야 합니까?

- [ ] A. PutObject에 s3:x-amz-acl 헤더 세트가 없는 경우 거부하도록 버킷 정책을 업데이트합니다.
- [ ] B. PutObject에 프라이빗으로 설정된 s3:x-amz-acl 헤더가 없는 경우 거부하도록 버킷 정책을 업데이트합니다.
- [ ] C. PutObject에 true로 설정된 aws:SecureTransport 헤더가 없는 경우 거부하도록 버킷 정책을 업데이트합니다.
- [ ] D. PutObject에 x-amz-server-side-encryption 헤더 세트가 없는 경우 거부하도록 버킷 정책을 업데이트합니다.

## Answer

정답: D

## Explanation

S3 버킷 정책에서 PutObject 요청에 x-amz-server-side-encryption 헤더가 없는 경우 거부(Deny)하도록 설정하면, 암호화 헤더 없이 업로드되는 모든 객체를 차단할 수 있습니다. 이 조건은 SSE-S3(AES256) 또는 SSE-KMS(aws:kms) 중 하나의 서버 측 암호화가 지정되지 않은 업로드를 거부하여 모든 객체의 암호화를 강제합니다.

오답 분석

A: s3:x-amz-acl 헤더는 객체의 접근 제어 목록(ACL)을 설정하는 헤더입니다. 암호화와는 전혀 관련이 없으므로 이 헤더의 존재 여부를 확인하는 것은 암호화를 보장하지 않습니다.

B: s3:x-amz-acl 헤더를 private으로 설정하는 것은 객체의 ACL을 비공개로 설정하는 것이지, 객체 암호화와는 무관합니다. ACL은 접근 권한을 제어하는 것이고, 암호화는 데이터 보호 메커니즘입니다.

C: aws:SecureTransport 헤더는 HTTPS를 통한 전송 중(in transit) 암호화를 강제하는 조건입니다. 이는 전송 계층 보안이며, S3에 저장되는 객체의 유휴 상태(at rest) 암호화와는 다른 개념입니다.

