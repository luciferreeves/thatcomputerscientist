# Shifoo (Previously _That Computer Scientist_)
Source Code for my Personal Website.

- Visit [shi.foo](https://shi.foo) to take a look at the current build.


```
                              README DEPRECATION NOTICE
                              -------------------------

Most of the specifications listed in this repository can be considered partially working. 
This is because the website (in general) needs to be running on a browser compatible 
with Windows XP or above or Mac OS X 10.6 or above. Although, our initial goal was to keep
the site backwards compatible with Windows 98 and Mac OS 9, I think a bit of javascript 
makes the site more livelier (o˘◡˘o).

I keep pushing updates to this repository, but take this readme with a grain of salt from 
now on. The instructions, in general, will work for local development, but don't expect the 
site to be compatible with HTML4 anymore lol.

I will be updating the readme soon (hopefully) to reflect the current state of the site.
```


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

