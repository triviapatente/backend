# Trivia Patente - Backend
##### Table of Contents
1. [Introduction](#intro)
2. [Getting started](#getstarted)
3. [Contributing](#contribute)
4. [Features](#features)
5. [License](#license)
6. [Acknowledgments](#acknowledgments)

<a name="intro"></a>
## Introduction
TriviaPatente is a mobile application that makes it easier and funnier to learn the theory of the driving license, connecting you with your friends.
This repository contains the webservice of the application.
[TODO A SCREENSHOT HERE OF SOMETHING COOL?]()

<a name="getstarted"><a/>
## Getting started

Set up the virtual environment (recommended)
ON MAC OS
```brew install postgresql@15```
```brew install libpq --build-from-source```
```brew install openssl@1.1```
```export LDFLAGS="-L/opt/homebrew/opt/postgresql@15/lib -L/opt/homebrew/opt/openssl@1.1/lib -L/opt/homebrew/opt/libpq/lib"```
```export CPPFLAGS="-I/opt/homebrew/opt/postgresql@15/include -I/opt/homebrew/opt/openssl@1.1/include -I/opt/homebrew/opt/libpq/include"```

Then,
```python -m venv .```
```pip install --upgrade pip```
```pip install --upgrade setuptools```
```pip install –-upgrade wheel```

```pip install -r requirements.txt```

Start postgres`
```export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"``
```createuser -P -s -e triviapatente``` with password triviapatente
```createdb triviapatente -O triviapatente```
```createdb triviapatente_test -O triviapatente```

```brew services run postgresql@15```




The code run and has been tested with {TODO VERSION OF IOS}. 
||Version|
|:----- |:----- |
|IOS|{TODO VERSION}|
|XCode|{IF MAKES SENSE}|
|OTHER PREREQUISITES?|{}|

### Installing
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
### Authors
This project was initially started by [Luigi Donadel](https://github.com/donadev).

<a name="license"><a/>
## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/triviapatente/backend/blob/master/LICENSE) file for details.
