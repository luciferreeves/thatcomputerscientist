FROM zenika/alpine-chrome:100-with-node

USER root

RUN apk add --no-cache msttcorefonts-installer fontconfig
RUN update-ms-fonts
RUN fc-cache -f && rm -rf /var/cache/*

USER chrome

COPY package*.json ./

RUN npm install

COPY . .
ENV PUPPETEER_EXECUTABLE_PATH='/usr/bin/chromium-browser'

EXPOSE 8080
CMD [ "node", "server.js" ]
