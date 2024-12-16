# Notepad

> 프로젝트 관련 패키지 설치
```
$ pip3 install -r requirements.txt
```

> Django 모델 -> 데이터베이스 마이그레이션
```
$ python3 manage.py makemigrations --settings=config.settings.development
$ python3 manage.py migrate --settings=config.settings.development
```

> 개발 환경 실행 명령어
```
$ python3 manage.py runserver --settings=config.settings.development
```

> 패키지 목록 조회 방법
```
$ pip3 freeze > requirements.txt
```