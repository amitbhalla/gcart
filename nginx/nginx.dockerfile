FROM nginx
WORKDIR /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/hello.conf /etc/nginx/conf.d/
EXPOSE 80