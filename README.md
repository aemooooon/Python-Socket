# Chat

## Introduction

It is a Chat application, which is Assignment 2 of IN608001 Intermediate Application Development Concepts in Semester one of 2021 by student Hua WANG and Lecturer Tom Clark.  Its based on Python 3 version, comes with socket, selectors package.  The Chat Server can listen multi-client request and also response each client and save relate information to local sqlite database.

## Environment

> Python 3+ need to be installed

## Get Started

1. Download repository with git command.

```bash
git clone git@github.com:OtagoPolytechnic/project-2-application-project-aemooooon.git
```

2. Start a ternimal in the root of repository folder.

3. Type `python Server.py` will start Chat server.

4. Start another terminal(one or more fine, the Application supported multi-client) to run client with command `python message_client.py`, you will see ` action > ` on terminal.

5. Type `login YourName` to login in Application. e.g. `login John`.

6. Type `send` will start send message to someone, follow the steps will type `to` who, then `Message` which is content of message, after that you can choose continue send to other one or just stop it.

7. Type `get` will get latest messages on screen. If it is your fisrt time to do that will display all of yours messages.

8. Type `logout` to logined out Application.

9. Type  `quit` to exit Application.

## Unit Testing

To do the unit test, you could use below command:

```bash
python Testing_RequestHandler.py
python Testing_User.py
python Testing_Message.py
```

## Notes

If you use MacOS might be using `python3 xxx` command, its depend on your Python version environment.