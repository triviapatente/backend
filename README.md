# Trivia Patente - Backend
##### Table of Contents
1. [Introduction](#intro)
2. [Getting started](#getstarted)
3. [Features](#features)
4. [Contributing](#contribute)
5. [Authors](#authors)
6. [License](#license)

<a name="intro"></a>
## Introduction

TriviaPatente is a mobile application that makes it easier and funnier to learn the theory of the driving license, connecting you with your friends.
This repository contains the native Android application.
|Screenshoots|||
|:----- |:----- |:----- |
|<img src="https://github.com/triviapatente/triviapatente.github.io/blob/main/images/screen1.png" alt="drawing" width="300"/>|<img src="https://github.com/triviapatente/triviapatente.github.io/blob/main/images/screen2.png" alt="drawing" width="300"/>|<img src="https://github.com/triviapatente/triviapatente.github.io/blob/main/images/screen3.png" alt="drawing" width="300"/>|

<a name="getstarted"><a/>
## Getting started

In order to run the backend, follow these steps:
ON MAC OS
- ```brew install postgresql@15```
- ```brew install libpq libpq-dev --build-from-source```
- ```brew install openssl@1.1```
- ```export LDFLAGS="-L/opt/homebrew/opt/postgresql@15/lib -L/opt/homebrew/opt/openssl@1.1/lib -L/opt/homebrew/opt/libpq/lib"```
- ```export CPPFLAGS="-I/opt/homebrew/opt/postgresql@15/include -I/opt/homebrew/opt/openssl@1.1/include -I/opt/homebrew/opt/libpq/include"```
- ```export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"```

Then,
- ```python -m venv .```
- ```pip install --upgrade pip```
- ```pip install --upgrade setuptools```
- ```pip install –-upgrade wheel```

- ```pip install -r requirements.txt```

Configure PostgreSQL
- ```brew services run postgresql@15```
- ```createuser -P -s -e triviapatente``` with password "triviapatente"
- ```createdb triviapatente -O triviapatente```
- ```createdb triviapatente_test -O triviapatente```



The code run and has been tested with {TODO VERSION OF IOS}. 
||Version|
|:----- |:----- |
|IOS|{TODO VERSION}|
|XCode|{IF MAKES SENSE}|
|OTHER PREREQUISITES?|{}|

<a name="installing"><a/>
### Installing
Before running the backend, you need to populate the database with questions and answers. This repository contains a crawler that gets from the internet ~7000 driver's license questions. The data is crawled from the website [https://www.patentati.it/](https://www.patentati.it/).

In order to run the crawler, type:

```python run_crawler.py```

### Deploying
### Testing

<a name="features"></a>
## Features
Maybe we should list some cool things such as:
+ security
+ sockets
+ ..

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
This project was developed with ❤️ and a giant dose of curiosity and passion from some very young folks (we were 20 at the time), in 2017 as a side project.
||Authors|
|:----- |:----- |
|<img src="https://avatars.githubusercontent.com/u/7453120?v=4" alt="drawing" width="50"/>|[Luigi Donadel](https://github.com/donadev)|
|<img src="https://avatars.githubusercontent.com/u/20773447?v=4" alt="drawing" width="50"/>|[Antonio Terpin](https://github.com/antonioterpin)|
|<img src="https://media.licdn.com/dms/image/C4D03AQGvkKpgIYl6jg/profile-displayphoto-shrink_200_200/0/1517931535631?e=1695859200&v=beta&t=uiddasmwI5VnP5TYdeuWd57geP_DArgR7vONoI901hk" alt="drawing" width="50"/>|[Gabriel Ciulei](https://www.linkedin.com/in/gabriel-ciulei)|

<a name="license"><a/>
## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/triviapatente/ios/blob/master/LICENSE) file for details.
