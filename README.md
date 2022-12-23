# That Computer Scientist
Source Code for my Personal Website.

## Specifications
- Server: [Nginx](https://www.nginx.com/)
- Language: [Python](https://www.python.org/), [HTML](https://www.w3schools.com/html/), [CSS](https://www.w3schools.com/css/), [JavaScript](https://www.javascript.com/)
- Framework: [Django](https://www.djangoproject.com/)
- Database: [Sqlite](https://www.sqlite.org/index.html)
- Deployment: [Oracle Cloud](https://www.oracle.com/cloud/)
- HTML Compatibility: [HTML4](https://www.w3.org/TR/html4/), [HTML5](https://www.w3.org/TR/html5/)
- CSS Compatibility: [CSS2](https://www.w3.org/TR/CSS2/), [CSS3](https://www.w3.org/TR/CSS3/)

## Installation
Install [Python](https://www.python.org/downloads/) and [NodeJS](https://nodejs.org/en/download/) (if you want to use the local server). Then install requirements:
```bash
pip install -r requirements.txt
```

Install localtunnel (will need to prefix with `sudo` on Linux and Mac):
```bash
npm install -g localtunnel
```

## Start the Server

> **Note**: This step uses [localtunnel](https://localtunnel.github.io/www/) to create a public URL for the server. This is only for development purposes. For production, use a proper web server like [Apache](https://httpd.apache.org/) or [Nginx](https://www.nginx.com/). Also, if you don't want to use the local tunnel, you can use the default Django server by running `python manage.py runserver`, but you will need to change the `CSRF_TRUSTED_ORIGINS`, `SESSION_COOKIE_DOMAIN`, and `DOMAIN_NAME` settings in `settings.py` accordingly.

First, make the `runserver.sh` file executable:
```bash
chmod +x runserver.sh
```

Then, run the server:
```bash
./runserver.sh
```

This will start the server which will be accessible at [https://thatcomputerscientist.loca.lt](https://thatcomputerscientist.loca.lt) (use `http` on older browsers). To stop the server, press `Ctrl+C`. The server will automatically restart when changes are made to the source code.

<!-- Footnotes -->
#### Footnotes

- [Archived Branch](https://github.com/luciferreeves/thatcomputerscientist/tree/archived) (Written in NodeJS + Express - **Status**: Basic Auth and APIs Implemented)
- For licensing information, please refer to the [LICENSE](LICENSE) file.

