# Trivia Patente - Backend
##### Table of Contents
- [Trivia Patente - Backend](#trivia-patente---backend)
        - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Getting started](#getting-started)
    - [Installing](#installing)
    - [Deploying](#deploying)
    - [Testing](#testing)
  - [Features](#features)
  - [Contribute](#contribute)
    - [Authors](#authors)
  - [License](#license)

<a name="intro"></a>
## Introduction

[TriviaPatente](https://triviapatente.github.io) is a mobile application ([iOS](https://github.com/triviapatente/ios), [Android](https://github.com/triviapatente/android)) that makes it easier and funnier to learn the theory of the driving license, connecting you with your friends.
This repository contains the native Android application.
|Screenshots|||
|:----- |:----- |:----- |
|<img src="https://github.com/triviapatente/triviapatente.github.io/blob/main/images/screen1.png" alt="drawing" width="300"/>|<img src="https://github.com/triviapatente/triviapatente.github.io/blob/main/images/screen2.png" alt="drawing" width="300"/>|<img src="https://github.com/triviapatente/triviapatente.github.io/blob/main/images/screen3.png" alt="drawing" width="300"/>|

<a name="getstarted"><a/>
## Getting started

In order to run the backend, follow these steps. 

On the M1/M2 chips, preliminary do
```console
brew install postgresql@15
brew install libpq libpq-dev --build-from-source
brew install openssl@1.1

export LDFLAGS="-L/opt/homebrew/opt/postgresql@15/lib -L/opt/homebrew/opt/openssl@1.1/lib -L/opt/homebrew/opt/libpq/lib"
export CPPFLAGS="-I/opt/homebrew/opt/postgresql@15/include -I/opt/homebrew/opt/openssl@1.1/include -I/opt/homebrew/opt/libpq/include"
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```

Clone the repo:
```console
git clone git@github.com:triviapatente/backend.git
```

Optionally, configure a virtual environment as
```console
cd backend
python -m venv .
pip install --upgrade pip
pip install --upgrade setuptools
pip install –-upgrade wheel
```
and install the dependencies with
```console
pip install -r requirements.txt
```

Finally, to configure the database, do:
```console
brew services run postgresql@15
createuser -P -s -e triviapatente``` with password "triviapatente
createdb triviapatente -O triviapatente
createdb triviapatente_test -O triviapatente
```

Notes:
+ In this project we considered the password "triviapatente". If you wish to use another username/password, you shall adapt the configurations in ```config.py```.
+ To run postgresql engine at computer startup automatically, use ```brew services start postgresql@15```.
+ To run postgresql on devices different than MacOS, check https://www.postgresql.org.

<a name="installing"><a/>
### Installing
Before running the backend, you need to populate the database with questions and answers. This repository contains a crawler that gets from the internet ~7000 driver's license questions. The data is crawled from the website [https://www.patentati.it/](https://www.patentati.it/):
```console
python run_crawler.py
```

### Deploying
To run the webservice, use
```console
python run.py
```

### Testing
To run all the tests, use
```console
python run_tests.py
```

<a name="features"></a>
## Features
This part of the project enjoys some features we were extremely proud at the time:
+ RESTful APIs and Websockets
+ Test Driven Development, test coverage of 100%
+ Role-based authentication
+ Push notifications

<a name="contribute"><a/>
## Contribute
We still need to set up an easy way to contribute, and provide a list of updates that might improve the project. You can save your ☕️s until then or, you
can drop an [email](mailto:luigi.donadel@gmail.com) to help us:
+ Set up coding style guidelines
+ Wiki
+ Documentation
+ Set up contribution workflow
<a name="authors"><a/>
### Authors
This project was developed with ❤️ and a giant dose of curiosity and passion from some very young folks (we were in our teens at the time), in 2017 as a side project.
||Authors|
|:----- |:----- |
|<img src="https://avatars.githubusercontent.com/u/7453120?v=4" alt="drawing" width="50"/>|[Luigi Donadel](https://luigidonadel.com)|
|<img src="https://avatars.githubusercontent.com/u/20773447?v=4" alt="drawing" width="50"/>|[Antonio Terpin](https://antonioterpin.com)|
|<img src="https://media.licdn.com/dms/image/C4D03AQGvkKpgIYl6jg/profile-displayphoto-shrink_200_200/0/1517931535631?e=1695859200&v=beta&t=uiddasmwI5VnP5TYdeuWd57geP_DArgR7vONoI901hk" alt="drawing" width="50"/>|[Gabriel Ciulei](https://www.linkedin.com/in/gabriel-ciulei)|

<a name="license"><a/>
## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/triviapatente/backend/blob/master/LICENSE) file for details.
