# Shifoo (Previously _That Computer Scientist_)
Source Code for my Personal Website.

- Visit [shi.foo](https://shi.foo) to take a look at the current build.

- ~~Visit [preview.thatcomputerscientist.com](https://preview.thatcomputerscientist.com) to see a instant live deployment of changes whenever I start changing something on my local machine. (_Availability of this server is not guaranteed as it is only active whenever I am working on the project_. Also, sometimes I keep the project loaded in my code editor, while being idle or doing something else – the link is viewable during this time as well.)~~

- `preview.thatcomputerscientist.com` is no longer available. The shell script [`runserver.sh`](runserver.sh) can be used to start a local server that presents two domain options:
    - `[*].peek.shi.foo` 
    - `[*].peek.thatcomputerscientist.com`

Both these domains point to `127.0.0.1` and its a matter of preference which one to choose. The script also automatically generates SSL certificates for both domains and starts the server with HTTPS enabled. A complete, example command chain now looks like:

![Example Command Chain](https://i.imgur.com/y3l6fJA.png)

## Screenshot
![Live Screenshot](https://shi.foo/ignis/screenshot)

> <sub><sup>_Screenshot served live from [shi.foo](https://shi.foo)'s server. For efficiency purposes, the screenshot is taken once per build and is served from the server's cache. The screenshot is updated whenever I push changes to this repository. Screenshots will generally be updated within 20 seconds after all GitHub Actions Workflows have completed._</sup></sub>

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

