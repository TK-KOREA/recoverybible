# 1. 가볍고 빠른 Nginx 웹 서버 이미지를 가져옵니다.
FROM nginx:alpine

# 2. nginx 프록시 설정 (rv.or.kr 중계)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 3. 내 컴퓨터의 index.html을 Nginx가 웹에 보여주는 기본 폴더로 복사합니다.
COPY index.html /usr/share/nginx/html/