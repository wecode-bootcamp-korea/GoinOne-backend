## Introduction
국내 암호화폐 거래소 [코인원](https://coinone.co.kr/) 클론 프로젝트

## 개발 인원 및 기간
- 개발기간 : 2020.03.09 ~ 2020.03.20 (2week)
- 개발인원 : 2 Front-End, 1 Back-End
- Github : [Front-End](https://github.com/wecode-bootcamp-korea/myfaketrip-frontend)<br/>
[Native](https://github.com/wecode-bootcamp-korea/GoinOne-app)

## 데모 영상 (이미지 클릭)
[![코인원](https://i.ytimg.com/vi/WL7wZg1-4xQ/hqdefault.jpg?sqp=-oaymwEZCNACELwBSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLCwkIHa79701hm2f8_HTqgXrnaKZQ)](https://www.youtube.com/watch?v=WL7wZg1-4xQ)

## 적용 기술
- Python
- Django Web Framework
- Bcrypt
- JWT
- MySQL
- AWS EC2, RDS
- Gunicorn
- CORS header
- Beautifulsoup, Selenium

## 구현 기능
### 인프라
- Amazon AWS 를 통한 배포
- EC2 인스턴스에 RDS 서버에 설치된 mysql 연동

### 계정
- 로그인 / 회원가입
- 이메일 / 패스워드 입력 값 검증
- 이메일 인증 (Google SMTP)
- JWT 토큰 발행 및 패스워드 해쉬화
- 고객 자산 조회

### 상품
- 매수/매도 기능
- 주문 내역 조회
- 거래 완료 내역 조회
- 24h Volume, 고가, 저가, 현재 가격 조회
- 코인 리스트 조회
- 차트 작성을 위한 과거 데이터 조회

## 데이터 모델링 ERD
![데이터모델링](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fk.kakaocdn.net%2Fdn%2FUniG7%2FbtqCZylwn8X%2FmjX0WBsymC2qkbSoy8Occ0%2Fimg.png)

