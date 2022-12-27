# That Computer Scientist
Source Code for my Personal Website.

- Visit [thatcomputerscientist.com](https://thatcomputerscientist.com) to take a look at the current build.

- Visit [preview.thatcomputerscientist.com](https://preview.thatcomputerscientist.com) to see a instant live deployment of changes whenever I start changing something on my local machine. (_Availability of this server is not guaranteed as it is only active whenever I am working on the project_. Also, sometimes I keep the project loaded in my code editor, while being idle or doing something else – the link is viewable during this time as well.)

## Specifications
- Server: [Nginx](https://www.nginx.com/)
- Language: [Python](https://www.python.org/), [HTML](https://www.w3schools.com/html/), [CSS](https://www.w3schools.com/css/), [JavaScript](https://www.javascript.com/)
- Framework: [Django](https://www.djangoproject.com/)
- Database: [Sqlite](https://www.sqlite.org/index.html)
- Deployment: [Oracle Cloud](https://www.oracle.com/cloud/)
- HTML Compatibility: [HTML4](https://www.w3.org/TR/html4/), [HTML5](https://www.w3.org/TR/html5/)
- CSS Compatibility: [CSS2](https://www.w3.org/TR/CSS2/), [CSS3](https://www.w3.org/TR/CSS3/)

## Installation
Install [Python](https://www.python.org/downloads/). Then install requirements:
```bash
pip install -r requirements.txt
```

## Start the Server

> **Note**: You will need to change the `CSRF_TRUSTED_ORIGINS`, `SESSION_COOKIE_DOMAIN`, and `DOMAIN_NAME` settings in `settings.py` accordingly.

To start the server, run:
```bash
python manage.py runserver
```

<!-- Footnotes -->
#### Footnotes

- [Archived Branch](https://github.com/luciferreeves/thatcomputerscientist/tree/archived) (Written in NodeJS + Express - **Status**: Basic Auth and APIs Implemented)
- For licensing information, please refer to the [LICENSE](LICENSE) file.

