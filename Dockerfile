FROM zenika/alpine-chrome:89-with-node-14

COPY package*.json ./

RUN npm install

COPY . .

ENV PUPPETEER_EXECUTABLE_PATH='/usr/bin/chromium-browser'

EXPOSE 8080
CMD [ "node", "server.js" ]
