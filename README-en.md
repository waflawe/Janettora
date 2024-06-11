# Janettora
A simple telegram bot for training English vocabulary, written in the framework
__[Aiogram](https://github.com/aiogram/aiogram)__. The project uses the relational DBMS __[PostgreSQL](https://github.com/postgres/postgres)__ as the main database,
non-relational DBMS __[Redis](https://github.com/redis/redis)__ for caching, library __[loguru](https://github.com/Delgan/loguru)__ for logging. Program
__[Docker](https://github.com/docker/compose)__'ized. The linter and code formatter used is __[ruff](https://github.com/astral-sh/ruff)__.

The bot `Janettora` has a built-in parser for the site [worderdict.ru](https://www.worderdict.ru/) and some small CLIs
utilities for database management.

__[Документация на русском](https://github.com/waflawe/Janettora/blob/main/README.md)__

<!-- TOC --><a name="table-of-contents"></a>
## Table of Contents
- [Janettora](#janettora)
  * [Content map](#table-of-contents)
  * [Quick start](#quick-start)
    + [Installation](#installation)
    + [Run in local development mode](#run-in-local-development-mode)
    + [Running in production mode via Docker](#running-in-production-mode-via-docker)
  * [Bot functionality](#bot-functionality)
  * [Screenshots](#screenshots)
  * [Description of settings](#settings-description)
    + [Runtime settings](#runtime-settings)
    + [Basic PostgreSQL database](#basic-postgresql-database)
    + [Main Redis database](#main-redis-database)
    + [Source PostgreSQL database for Docker](#source-postgresql-database-for-docker)
    + [Source SQLite database for Docker](#source-sqlite-database-for-docker)
  * [License](#license)
<!-- TOC --><a name="quick-start"></a>
## Quick start
<!-- TOC --><a name="installation"></a>
### Installation
```command line
git clone https://github.com/waflawe/Janettora.git
```
After successful installation, you need to decide on the word database to use. It is indicated to the program
differently depending on the running mode.
<!-- TOC --><a name="run-in-local-development-mode"></a>
### Running in local development mode
1. Install dependencies:
```command line
pip install -r requirements/dev.txt
```
2. Create a `.env` file and fill it in according to the example of the `.env.template` file. Description of settings [here](#settings-description).
3. For the bot to work, it needs a database of words containing data about their English, Russian versions and
parts of speech. To build it for local development mode, you have two paths provided by the program:
 - __Quick way__: you can use a small but ready-made database in the repository with the name
 `test_words.db`. It is used by default if you have not overridden the variable in the settings (`.env`)
 `SQLITE_WORDS_DB_TO_DOCKER_NAME`. To initialize it, enter the command `python database/cli/migrate_words.py` in
 project folder.
 - __Long alternative way__: you can use the site parser attached to the bot
 [worderdict.ru](https://www.worderdict.ru/), which will collect current data (until, of course, it is banned from your IP) about words into the database.
 To do this, run the command `python parser/parser.py` from the project folder.
4. If `Redis` is used local, then launch two terminal windows separately. Otherwise, skip this point.
In the first one, we launch `Redis`:
```command line
redis-server
```
5. In the second, we launch the project:
```command line
python bot/bot.py
```
6. After a long wait, go to the bot whose token we used in the `.env` file.
7. Enjoy.
<!-- TOC --><a name="running-in-production-mode-via-docker"></a>
### Running in production mode via Docker
1. Create a file `.env.docker` and fill it in according to the example of the file `.env.docker.template`. Description of settings [here](#settings-description).
2. For the bot to work, it needs a database of words containing data about their English, Russian versions and
parts of speech. To build it for production mode via Docker, you have two paths provided by the program:
 - __The fastest way__: do nothing. Then you will automatically use a small, but already ready
 database in a repository named `test_words.db`. It is used by default unless you override it in the settings
 (file `.env.docker`) variable `SQLITE_WORDS_DB_TO_DOCKER_NAME`.
 - __Long way__: you can use your `PostgreSQL` word database if it has a table with words in
 correct format (this, for example, could be a database previously used by the bot in
 [Run in local development mode](#run-in-local-development-mode), then section settings for you
 [Source PostgreSQL database for Docker](#source-postgresql-database-for-docker) will accordingly match the section settings
 [Basic PostgreSQL database](#basic-postgresql-database). This is, in principle, the most common case). If you have such a base, you can create
 the `.env` file, if you have not created it yet, set it up like `.env.template` (description of settings [here](#settings-description)) and,
 after setting the correct values ​​in the settings section [Source PostgreSQL database for Docker](#source-postgresql-database-for-docker), run
 command `python database/cli/collect_words.py`. The command will generate a `SQLite` database with the type name
 `collect_words_{GENERATION_DATE}.db` in the project root. Then enter the name of the generated database into the variable
 `SQLITE_WORDS_DB_TO_DOCKER_NAME` in the `.env.docker` file.
3. Run Docker-compose:
 ```command line
docker-compose up
```
4. After a long wait, go to the bot whose token we used in the `.env.docker` file.
5. Enjoy.
<!-- TOC --><a name="bot-functionality"></a>
## Bot functionality
In `Janettora` you can generate telegram quizzes asking you to guess the translation of an English word into Russian.
At the same time, the setup of these quizzes is quite flexible.

`Janettora` allows you to change your account settings, such as the number of answer options in quizzes
(`quiz_answers_count`) and parts of speech of words generated in quizzes (`words_part_of_speech`). When changing the setting
`quiz_answers_count` additionally changes the time given to complete the quiz. When using specific words
parts of speech in the `words_part_of_speech` setting, not only the generated word in English has a set part of speech,
but also all answer options in the quiz.

Also, `Janettora` can keep user statistics, such as the total number of completed quizzes, data on success
their completion (number of correct/incorrect answers, their ratio), statistics on the frequency of generation of quizzes with certain
settings (for example, how many times quizzes were generated, with `quiz_answers_count` equal to `3` and
`words_part_of_speech` equal to `Phrases`).
<!-- TOC --><a name="screenshots"></a>
## Screenshots
1. <img alt="Welcome message and keyboard" height="500" src=".githubscreenshots/hello-message-and-keyboard.png" width="500"/>
2. <img alt="Quiz" height="500" src=".githubscreenshots/quiz.png" width="500"/>
3. <img alt="Settings before" height="500" src=".githubscreenshots/settings-before.png" width="500"/>
4. <img alt="Settings after" height="500" src=".githubscreenshots/settings-after.png" width="500"/>
5. <img alt="Statistics" height="500" src=".githubscreenshots/statistics.png" width="500"/>
<!-- TOC --><a name="settings-description"></a>
## Description of settings
<!-- TOC --><a name="runtime-settings"></a>
### Runtime settings
- __TELEGRAM_BOT_TOKEN__  
Mandatory to change setting with telegram bot token. How to get it is described [here](https://tproger.ru/articles/telegram-bot-create-and-deploy#part1).

- __DEBUG__  
An optional setting that signals the importance of maintaining DEBUG logs (which, by the way, are kept in the `.logs/` folder). `1` - `True`, `0` - `False`.

### Main PostgreSQL database
- __DB_NAME__  
A non-changeable setting that specifies the name of the main `PostgreSQL` database for the bot.

- __DB_USER__  
Database username.

- __DB_PASSWORD__  
Database user password.

- __DB_HOST__  
Base IP address.

- __DB_PORT__  
Port on `DB_HOST` with the database.
### Main Redis database
- __REDIS_HOST__  
Base IP address.

- __REDIS_PORT__  
Port on `REDIS_HOST` with the database.

- __REDIS_DB_NUMBER__  
Base number. `0`+
### Source PostgreSQL database for Docker
Settings for the CLI utility `database/cli/collect_words.py`. Most often they coincide with the settings of the [Main PostgreSQL database]() section, but not always.
- __COLLECT_WORDS_DB_NAME__  
Base name.

- __COLLECT_WORDS_DB_USER__  
Database username.

- __COLLECT_WORDS_DB_PASSWORD__  
Database user password.

- __COLLECT_WORDS_DB_HOST__  
Base IP address.

- __COLLECT_WORDS_DB_PORT__  
Port on `DB_HOST` with the database.
### Source SQLite database for Docker
- __SQLITE_WORDS_DB_TO_DOCKER_NAME__  
The name `SQLite` of the database in the project folder with the word table for the Docker container. By default, the `test_words.db` database provided by the project itself is used.
## License <a name="license"></a>
This project is licensed under the [MIT License](https://github.com/waflawe/Janettora/blob/main/LICENSE).
