def message(domain, uidb64, token):
    return f"안녕하세요, 국내 암호화폐 거래소의 기준 GoinOne 입니다.\n\n아래 링크를 클릭하면 회원가입 인증이 완료됩니다.\n\n회원가입 링크 : http://{domain}/account/activate/{uidb64}/{token}\n\n감사합니다."