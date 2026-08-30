---
title: "Terraform 설치 및 초기 설정"
description: "Legacy study material imported from 01-iac-concepts/installation.md"
---

> **Archived study note / 기존 학습 노트**  
> 이 페이지는 기존 자료를 보존해 웹으로 가져온 문서입니다. 시험 기준은 [공식 목표 맵](/reference/exam-objectives/)과 [교정 노트](/reference/corrections/)를 우선하세요.  
> This page preserves the previous notes. Prefer the [official objective map](/reference/exam-objectives/) and [corrections](/reference/corrections/) when facts differ.

## 📦 Terraform 설치

### macOS

**방법 1: Homebrew (권장)**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

terraform version
```

**방법 2: 수동 설치**
```bash
wget https://releases.hashicorp.com/terraform/1.12.0/terraform_1.12.0_darwin_amd64.zip
unzip terraform_1.12.0_darwin_amd64.zip
sudo mv terraform /usr/local/bin/

terraform version
```

### Linux

**Ubuntu/Debian:**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

terraform version
```

**CentOS/RHEL:**
```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
sudo yum -y install terraform

terraform version
```

### Windows

**방법 1: Chocolatey**
```powershell
choco install terraform

terraform version
```

**방법 2: 수동 설치**
1. https://www.terraform.io/downloads 에서 Windows 버전 다운로드
2. 압축 해제 후 PATH에 추가
3. CMD 또는 PowerShell에서 `terraform version` 확인

---

## ⚙️ AWS CLI 설정

### 설치

**macOS:**
```bash
brew install awscli

aws --version
```

**Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

aws --version
```

**Windows:**
```powershell
choco install awscli

aws --version
```

### AWS Credentials 설정

```bash
aws configure

# 입력:
AWS Access Key ID [None]: YOUR_ACCESS_KEY_HERE
AWS Secret Access Key [None]: YOUR_SECRET_KEY_HERE
Default region name [None]: us-east-1
Default output format [None]: json
```

**확인:**
```bash
aws sts get-caller-identity

cat ~/.aws/credentials
cat ~/.aws/config
```

---

## 🔧 개발 도구 설정

### VS Code 확장

1. **HashiCorp Terraform**
   - Syntax highlighting
   - IntelliSense
   - 자동 완성

2. **Terraform**
   - Terraform 명령어 실행
   - 문법 검증

**설치:**
```bash
code --install-extension HashiCorp.terraform
```

### 기타 유용한 도구

**terraform-docs:**
```bash
brew install terraform-docs

terraform-docs markdown table . > README.md
```

**tflint:**
```bash
brew install tflint

tflint --init
tflint
```

**terragrunt:**
```bash
brew install terragrunt
```

---

## ✅ 설치 검증

```bash
terraform version

aws --version

aws sts get-caller-identity
```

**예상 출력:**
```
Terraform v1.12.0

aws-cli/2.15.0

{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-user"
}
```

---

다음: [첫 번째 Terraform 프로젝트](/archive/01-iac-concepts/first-project/)
