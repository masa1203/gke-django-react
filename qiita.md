# ゼロからGKEにDjango+Reactをデプロイする

## やりたいこと

Djagno+Reactの構成でアプリケーションを開発してGoogle Kubernetes Engineにデプロイしたいけれども
まとまったチュートリアルが有りそうで無かったので書きました。

ただ**まだ完全ではない点があると思います**が、少し経験がある方ならすぐに利用できるんじゃないかと思っています。

## 注意

これは未経験の趣味エンジニアがポートフォリオを作成するためにデプロイと格闘した記録です。
不備があれば何卒御指摘をお願い致します。。

## 目指す姿

[構成の絵]

## 環境

```sh
$ node --version
v12.14.1

$ npm --version
6.13.7

$ python --version
Python 3.7.4

$ docker --version
Docker version 19.03.8

OS windows10 pro
```

## まずはローカルで始める

### ディレクトリを作成する

```sh
# プロジェクトフォルダの作成
$ mkdir gke-django-tutorial
$ cd gke-django-tutorial
# ディレクトリを作成する
$\gke-django-tutorial\mkdir backend
$\gke-django-tutorial\mkdir frontend
```

### Backend の開発を始める

backendはDjango-rest-frameworkでRestAPIを作成します。
まずはbackendから環境を作成してみます。

```sh
# backendディレクトリに移動
$\gke-django-tutorial\cd backend
# Pythonの仮想環境作成
$\gke-django-tutorial\backend\python -m venv venv
# 仮想環境の有効化
$\gke-django-tutorial\backend\vnev\Scripts\activate
# Pythonパッケージのインストール
(venv)$\gke-django-tutorial\backend\python -m install --upgrade pip setuptools
(venv)$\gke-django-tutorial\backend\python -m install django djangorestframework python-dotenv
# Djangoのプロジェクトを始める
(venv)$\gke-django-tutorial\backend\django-admin startproject config .
```

backendディレクトリ下で`django-admin startprject config .`とすることで
`config`というDjangoプロジェクトフォルダが作成されました。

ローカルサーバーが起動するかどうか確認しましょう。

```sh
(venv)$\gke-django-tutorial\backend\python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 17 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
April 27, 2020 - 11:22:06
Django version 3.0.5, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

開発用サーバーが起動したので`http://localhost:8000/`にアクセスすると`The install worked successfully!`の画面が確認できます。

#### settings.py

`config/settings.py`を編集して基本的な設定を盛り込みます。
settings.py の秘匿すべき情報は`.env`ファイルに記述して公開しないようにします。
python-dotenv を使って`.env`に記載された情報を利用するように変更しましょう。

```sh
# .envファイルの作成
(venv)$\gke-django-tutorial\backend\type nul > .env
```

```python:config.settins.py
# config/settings.py

import os
from dotenv import load_dotenv  # 追加

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.basename(BASE_DIR)  # 追加

# .envの読み込み
load_dotenv(os.path.join(BASE_DIR, '.env'))  # 追加

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = ["*"]  # 変更


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 変更
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ja'  # 変更

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'


# 開発環境下で静的ファイルを参照する先
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # 追加

# 本番環境で静的ファイルを参照する先
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # 追加

# メディアファイルpath
MEDIA_URL = '/media/' # 追加

```

```sh:.env
# .env
SECRET_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
DEBUG = False
```

#### アプリケーションを追加する

todoアプリケーションを作っていきましょう。

```sh
(venv)$\gke-django-tutorial\backend\python manage.py startapp todo
```

`config/settings.py`の`INSTALLED_APPS`に`todo`と`rest_framework`を追加します。

```python
# config/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party
    'rest_framework',

    # Local
    'todo.apps.TodoConfig',
]

# 追加
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

```
`rest_framework.permissions.AllowAny`はdjango-rest-frameworkが暗黙的に決めているデフォルトの設定`'DEFAULT_PERMISSION_CLASSES'`を解除するためのものです。
この設定はまだよくわかってないのですがとりあえず前に進みます。

#### todo/models.py

`todo`アプリケーションmodelを作成します。

```python
# todo/models.py
from django.db import models


class Todo(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return self.title

```

`todo/admin.py`に作成したモデルを追加します。

```python
# todo/admin.py
from django.contrib import admin
from .models import Todo


admin.site.register(Todo)
```

マイグレーションします。

```sh
(venv)$\gke-django-tutorial\backend\python manage.py makemigrations
Migrations for 'todo':
  todo\migrations\0001_initial.py
    - Create model Todo

(venv)$\gke-django-tutorial\backend\python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, todo
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying sessions.0001_initial... OK
  Applying todo.0001_initial... OK
```

#### createsuperuser

管理者ユーザーを作成します。

```sh
(venv)$\gke-django-tutorial\backend\python manage.py createsuperuser
ユーザー名 (leave blank to use '[YOUR_NAME]'): admin
メールアドレス: YOUR_MAIL_ADDRESS@MAIL.COM
Password:
Password (again):
Superuser created successfully.
```

開発用サーバーを起動して`http://localhost:8000/admin`にアクセスするとDjango管理サイトログイン画面が表示されます。
先ほど設定したユーザー名、パスワードを入力してログインしてみましょう。

作成したアプリケーション`Todo`のテーブルを確認することができます。
2，3個アイテムを追加しておきましょう。

#### URLs

`config/urls.py`にtodoへのルーティングを追加します。

```python
# config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('todo.urls'))  # 追加
]

```

#### todo/urls.py

`todos/urls.py`を作成します。

```sh
(venv)$\gke-django-tutorial\backend\type nul > todo\urls.py
```

```python
# todo/urls.py
from django.urls import path, include
from .views import ListTodo, DetailTodo

urlpatterns = [
    path('<int:pk>/', DetailTodo.as_view()),
    path('', ListTodo.as_view())
]
```

#### todo/selializers.py

モデルインスタンスを簡単にjson形式に変換するためのシリアライザーを作成します。

```sh
(venv)$\gke-django-tutorial\backend\type nul > todo\serializers.py
```

```python
# todo/serializers.py
from rest_framework import serializers
from .models import Todo


class TodoSerializer(serizers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ('id', 'title', 'body')

```

`fields = ('id', 'title', 'text')`での`id`はmodelにて`PrimaryKey`を指定しない場合、
Django によって自動的に追加されます。

#### todo/views.py

Django Rest Frameworkで`views.py`を作成する場合は`rest_framework.generics`の`~~APIView`を継承します。

```python
# todo/views.py

from django.shortcuts import render
from rest_framework import generics
from .models import Todo
from .serializers import TodoSerializer


class ListTodo(generics.ListAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer


class DetailTodo(generics.RetrieveAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
```

routerなど設定できていませんが、とりあえずはTodoアイテムをAPIとして使用できるようになりました。
開発サーバーで`http://127.0.0.1:8000/api/`にアクセスするとAPIviewを確認することができます。

ここまではDjangoでよくあるローカル環境での開発です。

#### CORS

Django(`localhost:8000`)がReact(`localhost:3000`)とjson のやり取りをするには
CORS(Cross-Origin Resource Sharing)の設定を行う必要があります。

`django-cors-headers`をインストールしましょう。

```sh
(venv)$\gke-django-tutorial\backend\python -m pip install django-cors-headers
```

`config/settings.py`を更新します。

```python
# config/settings.py

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party
    'rest_framework',
    'corsheaders',

    # Local
    'todos.apps.TodosConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMidddleware',  # 追加
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

##################
# rest_framework #
##################

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
)
```

#### local_settings.py

`config/settings.py`は本番環境に使用することを考慮し、`config/local_settings.py`を作成してローカル開発用に分けておきます。
GKEデプロイ時にはCloudSQLを使用し、ローカルではsqlite3を使用するように、settings.pyを分けておくことで設定値を書き換えずに済みます。

```sh
# ファイルの作成
(venv)$\gke-django-tutorial\backend\type nul > config/local_settings.py
```

```python
# config/local_settings.py
from .settings import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

`config/local_settings.py`を使って開発用サーバーを起動しておきます。

```sh
(venv)$\gke-django-tutorial\backend\python manage.py runserver --settings config.local_settings
```

#### Tests

テストを書きます。

```python
# todos/test.py

from django.test import TestCase
from .models import Todo


class TodoModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Todo.objects.create(title="first todo", body="a body here")

    def test_title_content(self):
        todo = Todo.objects.get(id=1)
        excepted_object_name = f'{todo.title}'
        self.assertEqual(excepted_object_name, 'first todo')

    def test_body_content(self):
        todo = Todo.objects.get(id=1)
        excepted_object_name = f'{todo.body}'
        self.assertEqual(excepted_object_name, 'a body here')

```

```sh
(venv)$\gke-django-tutorial\backend\ python manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..
----------------------------------------------------------------------
Ran 2 tests in 0.007s

OK
Destroying test database for alias 'default'...
```

うまくいったようです。

#### 静的ファイル

デプロイ後に管理者機能のcssが反映されるように静的ファイルを集約しておきます。

```sh
# 静的ファイル用ディレクトリ
(venv)$\gke-django-tutorial\backend\mkdir static
# 静的ファイルの集約
(venv)$\gke-django-tutorial\backend\python manage.py collectstatic
```

#### requirements.txt

仮想環境にインストールしたPythonパッケージをrequirements.txtにまとめておきます。

```sh
# 静的ファイル用ディレクトリ
(venv)$\gke-django-tutorial\backend\python -m pip freeze > requirements.txt
```

実行するとbackend/下にrequirements.txtが作成されます。

```txt
asgiref==3.2.7
Django==3.0.5
django-cors-headers==3.2.1
djangorestframework==3.11.0
python-dotenv==0.13.0
pytz==2019.3
sqlparse==0.3.1
```

### Frontendの開発を進める

新しいコマンドプロンプトを開いてReactのプロジェクトを開始していきます。

```sh
# ディレクトリ下にReactプロジェクトをたてる
$\gke-django-tutorial\frontend\npx create-react-app .

# Reactの開発用サーバーを立ち上げる
$\gke-django-tutorial\frontend\yarn start
yarn run v1.22.0
$ react-scripts start
i ｢wds｣: Project is running at http://192.168.11.8/
i ｢wds｣: webpack output is served from
i ｢wds｣: Content not from webpack is served from C:\Users\masayoshi\docker_project\gke-django-tutorial_v2\frontend\public
i ｢wds｣: 404s will fallback to /
Starting the development server...
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.11.8:3000

Note that the development build is not optimized.
To create a production build, use yarn build.
```

`http://localhost:3000`にアクセスするとReactのWelcomeページが確認できます。

APIをリクエストするのには`axios`を使います。

```sh
# ライブラリのインストール
$\gke-django-tutorial\frontend\npm install axios --save
```

#### App.js

APIのエンドポイントは以下のような形でAPIを返してきます。

```javascript
import React, { Component } from 'react';
import axios from "axios";
import './App.css';

class App extends Component {
  state = {
    todo: []
  };

  componentDidMount() {
    this.getTodos();
  }

  getTodos() {
    axios
      .get("http://localhost:8000/api/")
      .then(res => {
        this.setState({ todo: res.data });
      })
      .catch(err => {
        console.log(err);
      });
  }
  render() {
    return (
      <div>
        {this.state.todo.map(item => (
          <div key={item.id}>
            <h1>{item.title}</h1>
            <p>{item.body}</p>
          </div>
        ))}
      </div>
    );
  }
}

export default App;

```

fronendからbarckendへのapiを叩いてtodoリスト一覧を表示させることができました。
これでローカルでの環境構築ができました。

## Docker化

次はこれをDocker化していきます。
frontend, backendそれぞれにDockerfileを作成してbackendコンテナ、frontendコンテナを作成します。
開発環境はdocker-composeで構築するように進めていきます。

docker-composeで立ち上げられるところまでを考えていきます。

### backendのDocker化

#### settings.py

backendをdockerコンテナ化する際に環境変数は`.env`で指定することができます。
これまでは`python-dotenv`で`.env`ファイルを参照していましたが、環境変数を参照するように
変更しましょう。

まずは`config/local_settings.py`を変更します。

```python
# config/local_settings.py
from .settings import *

SECRET_KEY = os.environ.get('SECRET_KEY')  # 追加

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

```python
# config/settings.py
import os

# SECRET_KEY = os.environ.get('SECRET_KEY')  # 削除

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG')

```

GKEデプロイ時にはCloudSQLを使用するのでその時にDATABASE部分は変更します。

#### Dockerfile

Dockerfileを作っていきます。

```sh
# Dockerfileの作成
$\gke-django-tutorial\backend\type nul > Dockerfile
```

```Dockerfile
# backend/Dockerfile

# set base image
FROM python:3.7

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
RUN mkdir /code
WORKDIR /code

# install dependencies
COPY requirements.txt /code/
RUN python3 -m pip install --upgrade pip setuptools
RUN pip install -r requirements.txt

# Copy project
COPY . /code/

EXPOSE 8000

```

#### .dockerignore

このままだと秘匿するべき`.env`ファイルも一緒にコピーされてしまいます。
`.dockerignore`を追加して`.env`が追加されないようにします。

```sh
$\gke-django-tutorial\backend\type nul > .dockerignore
```

```dockerfile
# .dockerignore
.env
```

#### docker-compose.yml

次にプロジェクトディレクトリにdocker-compose.ymlを設置して
docker-compose upでbackendコンテナを起動できるようにします。

```sh
# docker-composeの作成
$\gke-django-tutorial\type nul > docker-compose.yml
```

```yaml
# docker-compose.yml
version: "3.7"

services:
  backend:
    env_file: ./backend/.env
    build: ./backend/.
    command: python /code/manage.py runserver 0.0.0.0:8000 --settings /code/config.local_settings
    volumes:
      - ./backend:/code
    ports:
      - "8000:8000"
    stdin_open: true
    tty: true
    command: python /code/manage.py runserver 0.0.0.0:8000
    environment:
      - CHOKIDAR_USEPOLLING=true
```

さっそく起動してみましょう。

```sh
$\gke-django-tutorial\docker-compose up
Building backend
Step 1/10 : FROM python:3.7
 ---> b3b677605817

=省略=

Successfully built 153021f58015
Successfully tagged gke-django-tutorial_v2_backend:latest
WARNING: Image for service backend was built because it did not already exist. To rebuild this image you must use `docker-compose build` or `docker-compose up --build`.
Creating gke-django-tutorial_v2_backend_1 ... done
Attaching to gke-django-tutorial_v2_backend_1
backend_1  | Watching for file changes with StatReloader
backend_1  | Performing system checks...
backend_1  |
backend_1  | System check identified no issues (0 silenced).
backend_1  | April 28, 2020 - 14:07:07
backend_1  | Django version 3.0.5, using settings 'config.settings'
backend_1  | Starting development server at http://0.0.0.0:8000/
backend_1  | Quit the server with CONTROL-C.
backend_1  | Session data corrupted
```

「先に`docker-compose up --build`せい」とwarningが出ましたが無事に起動できました。
`http://localhost:8000/api/`にアクセスするとDjano Rest frameworkのAPI画面が確認できます。

### frontendのDocker化

つづいてfrontendのDocker化を行います。backendと同じようにfrontendディレクトリ下にDockerfileを作成し、docker-composeで起動させたいと思います。

```sh
# docker-composeの作成
$\gke-django-tutorial\frontend\type nul > Dockerfile
# .dockerignoreの作成
$\gke-django-tutorial\frontend\type nul > .dockerignore
```

#### Dockerfile

```Dockerfile
# frontend/Dockerfile
FROM node:12.14.1

RUN mkdir /code
WORKDIR /code

# Install dependencies
COPY package.json /code/
COPY package-lock.json /code/
RUN npm install

# Add rest of the client code
COPY . /code/

EXPOSE 3000

```

#### .dockerignore

frontend に関しては `node_modules/` が巨大であるため、これをマウントしたりコピーしたりするとかなりの時間を要します。
したがってfrontendの時と同じように`.dockerignore` を追加して node_modules をイメージビルドに使用しないようにしておきます。

```.dockerignore
node_modules
```

#### docker-compose.yml

```yaml
# docker-compose.yml
version: "3.7"

services:
  backend:
    env_file: ./backend/.env
    build: ./backend/.
    command: python /code/manage.py runserver 0.0.0.0:8000 --settings /code/config.local_settings
    volumes:
      - ./backend:/code
    ports:
      - "8000:8000"
    stdin_open: true
    tty: true
    command: python /code/manage.py runserver 0.0.0.0:8000
    environment:
      - CHOKIDAR_USEPOLLING=true
  frontend:
    build: ./frontend/.
    volumes:
      - ./frontend:/code
      - /code/node_modules
    ports:
      - "3000:3000"
    command: yarn start
    stdin_open: true
    tty: true
    environment:
      - CHOKIDAR_USEPOLLING=true
      - NODE_ENV=development
    depends_on:
      - backend
```

frontendの`depends_on`とすることでbackendコンテナが立ち上がったあとにfrontendコンテナが
起動するようになります。

environment に`CHOKIDAR_USEPOLLING=true`を追加することでイメージを再ビルドすることなく
ホットリローディングしてくれるようになります。

さっそくビルドしてコンテナを起動し直してみます。


```sh
# docker-composeの作成
$\gke-django-tutorial\docker-compose up --build
```

ビルドに時間がかかりますが、問題なく起動することができました。
`http://localhost:3000`にアクセスすると元の画面が確認できます。

## デプロイ

GKEにデプロイしていきます。公式チュートリアルと被るところもあるかと思います。

### プロジェクトを作成

コンソールから新しいプロジェクトを開始します。

プロジェクト名: gke-django-tutorial
場所: 組織なし

### 課金が有効かどうかを確認する

参考 : https://cloud.google.com/billing/docs/how-to/modify-project?authuser=2

### Cloud SDKをインストールして初期化

```sh
$\gke-django-tutorial\gcloud init

Welcome! This command will take you through the configuration of gcloud.

Pick configuration to use:
 [1] Re-initialize this configuration [xxxxxx] with new settings
 [2] Create a new configuration

Please enter your numeric choice:  2

Enter configuration name. Names start with a lower case letter and
contain only lower case letters a-z, digits 0-9, and hyphens '-':  gke-django-tutorial
Your current configuration has been set to: [gke-django-tutorial]

You can skip diagnostics next time by using the following flag:
  gcloud init --skip-diagnostics

Network diagnostic detects and fixes local network connection issues.
Checking network connection...done.
Reachability Check passed.
Network diagnostic passed (1/1 checks passed).

Choose the account you would like to use to perform operations for
this configuration:
 [1] XXXX@gmail.com
 [2] YYYY@gmail.com
 [3] Log in with a new account
Please enter your numeric choice:  1

You are logged in as: [XXXX@gmail.COM].

Pick cloud project to use:
 [1] XXXXXXX
 [2] [YOUR_PROJECT]
 [3] Create a new project
Please enter numeric choice or text value (must exactly match list
item):  2

Your current project has been set to: [YOUR_PROJECT].

Not setting default zone/region (this feature makes it easier to use
[gcloud compute] by setting an appropriate default value for the
--zone and --region flag).
See https://cloud.google.com/compute/docs/gcloud-compute section on how to set
default compute region and zone manually. If you would like [gcloud init] to be
able to do this for you the next time you run it, make sure the
Compute Engine API is enabled for your project on the
https://console.developers.google.com/apis page.

Your Google Cloud SDK is configured and ready to use!

* Commands that require authentication will use komedapeople@gmail.com by default
* Commands will reference project `[YOUR_PROJECT]` by default
Run `gcloud help config` to learn how to change individual settings

This gcloud configuration is called [YOUR_PROJECT]. You can create additional configurations if you work with multiple accounts and/or projects.
Run `gcloud topic configurations` to learn more.

Some things to try next:

* Run `gcloud --help` to see the Cloud Platform services you can interact with. And run `gcloud help COMMAND` to get help on any gcloud command.
* Run `gcloud topic --help` to learn about advanced features of the SDK like arg files and output formatting


Updates are available for some Cloud SDK components.  To install them,
please run:
  $ gcloud components update



To take a quick anonymous survey, run:
  $ gcloud survey

```

### 必要なAPIを有効にする

Datastore, Pub/Sub, Cloud Storage JSON, Cloud Logging, and Google+APIs を有効にします。

### CloudSQLの準備

#### Cloud SQL Adminを有効にする

```sh
$\gke-django-tutorial\gcloud services enable sqladmin
Operation "operations/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" finished successfully.
```

#### CloudSQL proxy

Cloud SQL Proxyをダウンロードして`cloud_sql_proxy.exe`に名前を変更します。
参考: https://cloud.google.com/python/django/kubernetes-engine#installingthecloudsqlproxy

#### インスタンスの作成

CloudSQLインスタンスを作成します。

```sh
データベースエンジンの選択: PostgreSQL
インスタンスID: [DB_ID]
パスワード: [YOUR_PASSWORD]
ロケーション:
    リージョン: [DB_REGION]
    ゾーン: [DB_ZONE]
データベースのバージョン: PostgreSQL 11
```

#### インスタンスの初期化

先ほどダウンロードした`cloud_sql_proxy.exe`を使ってCloudSQLに接続するための`connectionName`を確認します。

```sh
# connecsionNameの確認
$\gke-django-tutorial\gcloud sql instances describe db_sample
connectionName: [YOUR_PROJECT]:[DB_REGION]:[DB_ID]

# インスタンスの接続
$\gke-django-tutorial\gcoud_sql_proxy.exe -instances="[YOUR_PROJECT]:[DB_REGION]:[DB_ID]"=tcp:5432
2020/04/28 17:49:51 Listening on 127.0.0.1:5432 for gke-django-tutorial:asia-northeast1:websql
2020/04/28 17:49:51 Ready for new connections
```

このコマンドによって手元のPCからCloudSQLインスタンスに接続することができました。

#### データベースの作成

コンソールからデータベースを作成しましょう。コンソール上の`websql`を選択して`データベース`から`データベースを作成`することができます。

```sh
データベース名: [DATABASE_NAME]
```

#### データベースユーザーの作成

データベースのユーザーアカウントを作成しておきます。
```sh
ユーザー名: [DATABASE_USER]
パスワード: [DATABASE_PASSWORD]
```

#### CloudSQLのサービスアカウントの作成

CloudSQlのサービスアカウントを作成して、json形式のプライベートキーをダウンロードしましょう。

```sh
サービスアカウント名: [SERVICE_ACCOUNT_NAME]
サービスアカウントID: [SERVICE_ACCOUNT_NAME]@BBBBBBBBB.iam.gservice
権限: Cloud SQL 管理者
⇒キーの作成でjson形式を選択
```

```sh
$\gke-django-tutorial\mkdir secrets
```

プライベートキーはプロジェクト直下に`secrets\cloudsql`というディレクトリを作成して設置しました。

#### 環境変数の設定

DjangoのデータベースをCloudSQLに設定して起動していきたいと思います。
`DATABASE_USER`と`DATABASE_PASSWORD`を環境変数として利用するため、`.env`ファイルに追加します。
keyとvalueの間にスペースを置かないようにしましょう。

```sh
SECRET_KEY='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
DEBUG=False
DATABASE_USER=master
DATABASE_PASSWORD=websql-pass
```

#### Pythonパッケージの追加

DjangoからPostgresを使用するにはパッケージを追加する必要があります。
デプロイに必要なパッケージを追加しておきます。

```sh
# パッケージのインストール
(venv)$\gke-django-tutorial\backend\python -m pip install wheel gunicorn psycopg2-binary

# requirements.txtの更新
(venv)$\gke-django-tutorial\backend\python -m pip freeze > requirements.txt
```

#### backend/config/settings.py

DjangoのDATABASE設定をdb.sqlite3からCloudSQLに変更します。
`.env`ファイルを直接参照する必要があるため、`Python-dotenv`を使って読み込みます。

```python
# backend/config/setting.sy

import os
from dotenv import load_dotenv  # 追加

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.basename(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))  # 追加

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG')

DATABASES = {
    'default': {
        # If you are using Cloud SQL for MySQL rather than PostgreSQL, set
        # 'ENGINE': 'django.db.backends.mysql' instead of the following.
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'web-db',
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

#### マイグレーション

データベースがCloudSQLに変更したのでマイグレーションし直す必要があります。

```sh
(venv)$\gke-django-tutorial\backend\python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, todo
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying sessions.0001_initial... OK
  Applying todo.0001_initial... OK
```

問題なくCloudSQLにマイグレーションすることができました。

#### 管理ユーザーの追加

sqlite同様に管理ユーザーを作成します。

```sh
(venv)$\gke-django-tutorial\backend\python manage.py createsuperuser
ユーザー名 (leave blank to use '[YOUR_NAME]'): [SUPERUSER_NAME]
メールアドレス: [YOUR_EMAIL]@gmail.com
Password:
Password (again):
Superuser created successfully.
```

開発用サーバーを立ち上げてadminページからデータを3つほど追加しておきましょう。

```sh
(venv)$\gke-django-tutorial\backend\python manage.py runserver
```

### Cloud Storageの準備

静的ファイルをGoogle Cloud Storageに格納するための設定を行います。
ストレージを作成して静的ファイルをアップロードします。これをしないとadmin画面などのcssが反映されません。

```sh
# ストレージの作成
(venv)$\gke-django-tutorial\backend\gsutil mb gs://[STORAGE_NAME]
Creating gs://gke-django-storage/...

# 公開設定
(venv)$\gke-django-tutorial\backend\gsutil defacl set public-read gs://[STORAGE_NAME]
Setting default object ACL on gs://[STORAGE_NAME]/...
/ [1 objects]

# 静的ファイルを集める
(venv)$\gke-django-tutorial\backend\python manage.py collectstatic

# Cloud Storageに静的ファイルをアップロードする
(venv)$\gke-django-tutorial\backend\gsutil rsync -R staticfiles/ gs://[STORAGE_NAME]/static

```

`backend/config/settings.py`の`STATIC_URL`をGCSを参照するように変更します。

```python
# backend/config/settings.py
STATIC_URL = 'https://storage.googleapis.com/[STORAGE_NAME]/static/'
```

### クラスター作成

クラスターを作成してコンテナをデプロイします。ServiceとIngressを設定することで外部からアクセスすることが可能になります。

コンソールからクラスタを作成します。

```sh
クラスター名: [K8S_CLUSTER]
ロケーションタイプ:ゾーン:[K8S_CLUSTER_ZONE]
マスターのバージョン: 1.14.10-gke.27(デフォルト)
```

### contextsの入手

作成したクラスターをローカルのkubectlから利用するためにcontextsを入手します。

```sh
$\gke-django-tutorial\gcloud container clusters get-credentials [K8S_CLUSTER] --zone="[K8S_CLUSTER_ZONE]"
Fetching cluster endpoint and auth data.
kubeconfig entry generated for [K8S_CLUSTER].

# コンテキストが適用されているかどうかを確認する。
$\gke-django-tutorial\kubectl config current-context
```

### Secrets

秘匿すべき変数はSecretsリソースに登録して使用します。

#### Cloud SQL

Secretsを利用することでCloudSQLのユーザー名、パスワードを環境変数として安全に使用することができます。
GKE から Cloud SQL のインスタンスを使用するにあたって、インスタンスレベルアクセスとデータベースアクセスに関するSecretsを作成する必要があります。

参考: [インスタンスのアクセス制御]:(https://cloud.google.com/sql/docs/mysql/instance-access-control)

インスタンスレベルのアクセスについてSecretsを作成します。

```sh
$\gke-django-tutorial\kubectl create secret generic cloudsql-oauth-credentials --from-file=credentials.json=".\secrets\cloudsql\ZZZZZZZZZZZZZZZ.json"

secret/cloudsql-oauth-credentials created
```

データベースへアクセスに関する secret を作成します。

```sh
$\gke-django-tutorial\kubectl create secret generic cloudsql --from-literal=username="[DATABASE_USER]" --from-literal=password="[DATABASE_PASSWORD]"
```

#### SECRET_KEY

`.env`ファイルに記述されている残りの`SECRET_KEY`をSecretsに追加しましょう。
`backend/config/settings.py`の`DEBUG`はFalseとしておきます。

```sh
$\gke-django-tutorial\kubectl create secret generic secret-key --from-literal=SECRET_KEY="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

`backend/config/settings.py`で関係のある個所は以下のような状態になります。

```python
# backend/config/settings.py

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.basename(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')  # 変更

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    'default': {
        # If you are using Cloud SQL for MySQL rather than PostgreSQL, set
        # 'ENGINE': 'django.db.backends.mysql' instead of the following.
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'web-db',
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

```

### コンテナイメージのビルド

ローカルでイメージをビルドしてGoogle Cloud Registryにアップロードします。
イメージ名は`gcr.io/${PROJECT}/${IMAGENAME}:${TAGNAME}`形式にする必要があります。

```sh
# プロジェクト名の確認
$\gke-django-tutorial\gcloud config get-value project
Your active configuration is: [YOUR_PROJECT]
gke-django-tutorial

# イメージのビルド
# backend
$\gke-django-tutorial\docker image build --no-cache -t gcr.io/[YOUR_PROJECT]/backend:latest ./backend

# frontend
$\gke-django-tutorial\docker image build --no-cache -t gcr.io/[YOUR_PROJECT]/frontend:latest ./frontend
```

```sh
# イメージをGCRにアップロードする
# backend
$\gke-django-tutorial\gcloud docker -- push gcr.io/[YOUR_PROJECT]/backend:latest
WARNING: `gcloud docker` will not be supported for Docker client versions above 18.03.

As an alternative, use `gcloud auth configure-docker` to configure `docker` to
use `gcloud` as a credential helper, then use `docker` as you would for non-GCR
registries, e.g. `docker pull gcr.io/project-id/my-image`. Add
`--verbosity=error` to silence this warning: `gcloud docker
--verbosity=error -- pull gcr.io/project-id/my-image`.

See: https://cloud.google.com/container-registry/docs/support/deprecation-notices#gcloud-docker

The push refers to repository [gcr.io/[YOUR_PROJECT]/backend]
12ed78fdfd14: Pushed
485427ae6881: Pushed
bb530f6bab17: Pushed
4eae8da6dc9e: Pushed
a91544cdf6ea: Pushed
956d28316107: Layer already exists
86120ec29f78: Layer already exists
5d34cecc2826: Layer already exists
baf481fca4b7: Layer already exists
3d3e92e98337: Layer already exists
8967306e673e: Layer already exists
9794a3b3ed45: Layer already exists
5f77a51ade6a: Layer already exists
e40d297cf5f8: Layer already exists
latest: digest: sha256:3905957cfddea8454288b460adf8b134d0de1bc0791dbc8cf3fe7b9e6012512f size: 3267

# frontend
$\gke-django-tutorial\gcloud docker -- push gcr.io/[YOUR_PROJECT]/frontend:latest
WARNING: `gcloud docker` will not be supported for Docker client versions above 18.03.

As an alternative, use `gcloud auth configure-docker` to configure `docker` to
use `gcloud` as a credential helper, then use `docker` as you would for non-GCR
registries, e.g. `docker pull gcr.io/project-id/my-image`. Add
`--verbosity=error` to silence this warning: `gcloud docker
--verbosity=error -- pull gcr.io/project-id/my-image`.

See: https://cloud.google.com/container-registry/docs/support/deprecation-notices#gcloud-docker

The push refers to repository [gcr.io/[YOUR_PROJECT]/frontend]
c6c151685fbb: Pushed
ef3845fc4e9d: Pushed
069d14dab7a7: Pushed
a3a63dfb31f4: Pushed
2fcc481d7fdd: Pushed
203542cdccd7: Pushed
37d4010f40f0: Pushed
f895d244bc8e: Pushed
03dc1830d2d5: Pushed
1d7382716a27: Pushed
01727b1a72df: Layer already exists
69dfa7bd7a92: Layer already exists
4d1ab3827f6b: Layer already exists
7948c3e5790c: Layer already exists
latest: digest: sha256:26d0836290483f2f58141db9bd18a66a5c5b99a3ce9da3643679592d0d8bb5ec size: 3261

```

### Frontendのデプロイ

FrontendのDeploymentを作成してデプロイします。deploymentとして`frontend-react.yml`というファイルを作成します。

```sh
$\gke-django-tutorial\type nul > frontend-deployment.yml
```

```yml
# frontend-deployment.yml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: frontend
  labels:
    app: frontend
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: gcr.io/[YOUR_PROJECT]/frontend:latest
          imagePullPolicy: Always
          command: ["npm", "start"]
          ports:
          - containerPort: 3000

```

```sh
# Deploymentをデプロイ
$\gke-django-tutorial\kubectl create -f frontend-deployment.yml
deployment.extensions/frontend created

# 確認
$\gke-django-tutorial\kubectl get pods
NAME                        READY   STATUS              RESTARTS   AGE
frontend-77f75d4c47-lgzv6   0/1     CrashLoopBackOff   6          9m39s
```

#### CrashLoopBackOff

`STATUS`が`CrashLoopBackOff`となってしましました。ログを確認してみます。

```sh
$ kubectl logs frontend-77f75d4c47-lgzv6

> frontend@0.1.0 start /code
> react-scripts start

[34mℹ[39m [90m｢wds｣[39m: Project is running at http://XX.XX.X.X/
[34mℹ[39m [90m｢wds｣[39m: webpack output is served from
[34mℹ[39m [90m｢wds｣[39m: Content not from webpack is served from /code/public
[34mℹ[39m [90m｢wds｣[39m: 404s will fallback to /
Starting the development server...
```

Reactの環境構築周りに問題があるらしいことがわかります。
- [stack overflow : GKE deployment ReactJS app CrashLoopBackoff](https://stackoverflow.com/questions/61463529/gke-deployment-reactjs-app-crashloopbackoff)

これを参考にすると、どうやら`react-scripts`が悪さをしているようです。

`frontend\package-lock.json`を確認すると`react-scripts`のバージョンは`3.4.1`でした。
`3.4.0`でインストールし直したあと、もう一度デプロイします。

```sh
# 3.4.1をアンインストール
$\gke-django-tutorial\frontend\npm uninstall react-scripts@3.4.1

# 3.4.0をインストール
$\gke-django-tutorial\frontend\npm install react-scripts@3.4.0 --save

# frontendコンテナイメージの再ビルド
$\gke-django-tutorial\docker image build --no-cache -t gcr.io/[YOUR_PROJECT]/frontend:latest ./frontend

# GCRへのアップロード
$\gke-django-tutorial\gcloud docker -- push gcr.io/[YOUR_PROJECT]/frontend:latest

# frontendのDeploymentを作成
$\gke-django-tutorial\kubectl apply -f frontend-deployment.yml

# 確認
$\gke-django-tutorial\kubectl get pods

```

問題なくfrontendのPodがデプロイできていることが確認できました。

### Backendのデプロイ

frontendと同じようにbackendのDeploymentを作成してデプロイします。

`backend-deployment.yml`を作成します。

```sh
$\gke-django-tutorial\type nul > backend-deployment.yml
```

```yml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: backend
  namespace: default
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: gcr.io/[YOUR_PROJECT]/backend:v1
          imagePullPolicy: Always
          env:
            - name: DATABASE_USER
              valueFrom:
                secretKeyRef:
                  name: cloudsql
                  key: username
            - name: DATABASE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: cloudsql
                  key: password
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: secret-key
                  key: SECRET_KEY
          ports:
            - containerPort: 8000

        - image: gcr.io/cloudsql-docker/gce-proxy:1.16
          name: cloudsql-proxy
          command:
            [
              "/cloud_sql_proxy",
              "--dir=/cloudsql",
              "-instances=[YOUR_PROJECT]:[DB_REGION]:[DB_ID]=tcp:5432",
              "-credential_file=/secrets/cloudsql/credentials.json",
            ]
          volumeMounts:
            - name: cloudsql-oauth-credentials
              mountPath: /secrets/cloudsql
              readOnly: true
            - name: ssl-certs
              mountPath: /etc/ssl/certs
            - name: cloudsql
              mountPath: /cloudsql
      volumes:
        - name: cloudsql-oauth-credentials
          secret:
            secretName: cloudsql-oauth-credentials
        - name: ssl-certs
          hostPath:
            path: /etc/ssl/certs
        - name: cloudsql
          emptyDir:
```

Django側で必要な環境変数を作成したSecretSから参照していることが確認できます。
backendのイメージは既に作成してGCRにpushしてあるので、早速デプロイします。

```sh
# backendのデプロイ
$\gke-django-tutorial\kubectl create -f backend-deployment.yml

# 確認
$\gke-django-tutorial\kubectl get pods
NAME                        READY   STATUS    RESTARTS   AGE
backend-989b96b5-ldc9b      2/2     Running   0          35s
frontend-77f75d4c47-f2fdl   1/1     Running   0          28m

$\gke-django-tutorial\kubectl logs backend-989b96b5-ldc9b backend
[2020-04-29 14:55:11 +0000] [1] [INFO] Starting gunicorn 20.0.4
[2020-04-29 14:55:11 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
[2020-04-29 14:55:11 +0000] [1] [INFO] Using worker: sync
[2020-04-29 14:55:11 +0000] [8] [INFO] Booting worker with pid: 8

$\gke-django-tutorial\kubectl logs backend-989b96b5-ldc9b cloudsql-proxy
2020/04/29 14:55:10 current FDs rlimit set to 1048576, wanted limit is 8500. Nothing to do here.
2020/04/29 14:55:10 using credential file for authentication; email=XXXXX@gke-django-tutorial.iam.gserviceaccount.com
2020/04/29 14:55:10 Listening on 127.0.0.1:5432 for gke-django-tutorial:asia-northeast1:websql
2020/04/29 14:55:10 Ready for new connections

```

STATUSがRunningになっているのんで問題なさそうです。

### Serviceの追加

ServiceタイプをLoadBalancerにするかExternalNameにして外部公開する方法がありますが、
今回はIngressを使ってServiceを公開する構成にしたいと思います。

ServiceもDeploymentと同様、yml形式で宣言ファイルを作成し、kubectlでGKEにリソースを追加することができます。

```sh
# ファイルの作成
\gke-django-tutorial\type nul > service.yml
```

```yml:service.yml
kind: Service
apiVersion: v1
metadata:
  name: frontend-node-service
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
    - port: 3000
      targetPort: 3000
      protocol: TCP
---
kind: Service
apiVersion: v1
metadata:
  name: backend-node-service
spec:
  type: NodePort
  selector:
    app: backend
  ports:
    - port: 8000
      targetPort: 8000
      protocol: TCP

```

ServiceタイプをNodePortとしました。
外部からのリクエストはIngressのLoadBalancerがServiceに転送し、Serviceはノードの8000ポート(backend-Django)に転送しています。

```sh
# Serviceの追加
\gke-django-tutorial\kubectl create -f service.yml
service/frontend-node-service created
service/backend-node-service created

# Serviceの確認
\gke-django-tutorial\kubectl get services
NAME                    TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)          AGE
backend-node-service    NodePort    10.28.5.61   <none>        8000:31332/TCP   32s
frontend-node-service   NodePort    10.28.8.91   <none>        3000:31535/TCP   35s
kubernetes              ClusterIP   10.28.0.1    <none>        443/TCP          22h
```

### Ingressの追加

HTTP(S)ロードバランサを作成するIngressを使ってアプリケーションを公開します。

```sh
# Ingressの追加
\gke-django-tutorial\type nul > ingress.yml
```

Ingressの実態はIngressコントローラーであり、Ingressコントローラーは指定することができます。
GKEでIngressコントローラーを指定しない場合、デフォルトでCloud LoadBalancerが適用されます。
今回はデフォルトで進めていきます。

```yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-service
  namespace: default
  annotations:
    kubernetes.io/ingress.class: gce

spec:
  rules:
    - http:
      paths:
      - path: /*
        backend:
          serviceName: frontend-node-service
          servicePort: 3000
      - path: /api/*
        backend:
          serviceName: backend-node-service
          servicePort: 8000
      - path: /admin/*
        backend:
          serviceName: backend-node-service
          servicePort: 8000
```

```sh
# Ingressの追加
\gke-django-tutorial\kubectl create -f ingress.yml
ingress.extensions/ingress-service created

# 確認
\gke-django-tutorial\kubectl get ingress
NAME              HOSTS   ADDRESS        PORTS   AGE
ingress-service   *       34.95.105.61   80      112s
```

これで外部へ公開ができたと思いきや、コンソールを確認すると`backend services are in UNHEALTHY state`なるメッセージが確認できます。

#### backendへのヘルスチェックに対応する

外部公開するIngressを通して公開されるServiceはロードバランサからのヘルスチェックに応答する必要があります。
このヘルスチェックはデフォルトでは`/`パスに対するGETリクエストに対し、HTTP200ステータスのレスポンスを期待しています。
frontendのReact側では`/`パスに対してHTTP200ステータスを返答しますが、backendのDjango側では`/`への返答は追加していません。

今回はヘルスチェックへのパスを`/api/healthz`に変更し、Djangoは`/api/healthz`に対してHTTP200ステータスを返答するように追加します。

参考:
- [Ingress for GKE ヘルスチェック](https://cloud.google.com/kubernetes-engine/docs/concepts/ingress?hl=ja#health_checks)

- [Ingress でヘルスチェックのリクエスト先を変更する](https://qiita.com/nirasan/items/24858dfa03883cd4aa79)

- [【GKE】Ingressのヘルスチェックで All backend services are in UNHEALTHY stateが出る場合の原因と解決方法](https://qiita.com/arthur_foreign/items/9e7a2cf4360ffcefcc9a#nuxtjs%E3%81%AEexpress%E3%81%A7health%E3%81%AE%E3%83%91%E3%82%B9%E3%81%AB%E3%83%AA%E3%82%AF%E3%82%A8%E3%82%B9%E3%83%88%E3%81%8C%E9%A3%9B%E3%82%93%E3%81%A0%E3%82%89200%E3%81%AE%E3%82%B9%E3%83%86%E3%83%BC%E3%82%BF%E3%82%B9%E3%82%B3%E3%83%BC%E3%83%89%E3%82%92%E8%BF%94%E3%81%99)

##### Deployment

DeploymentにはLivenessProbeとReadinessProbeを追加してデプロイし直しましょう。

```yml
# backend-deployment.yml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: backend
  labels:
    app: backend
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: gcr.io/[YOUR_PROJECT]/backend:latest
        imagePullPolicy: Always
        command: ["gunicorn", "-b", ":8000", "config.wsgi"]
        env:
          - name: DATABASE_USER
            valueFrom:
              secretKeyRef:
                name: cloudsql
                key: username
          - name: DATABASE_PASSWORD
            valueFrom:
              secretKeyRef:
                name: cloudsql
                key: password
          - name: SECRET_KEY
            valueFrom:
              secretKeyRef:
                name: secret-key
                key: SECRET_KEY
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /api/healthz
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /api/healthz
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 6

      - image: gcr.io/cloudsql-docker/gce-proxy:1.16
        name: cloudsql-proxy
        command:
          [
            "/cloud_sql_proxy",
            "--dir=/cloudsql",
            "-instances=[YOUR_PROJECT]:[DB_REGION]:[DB_ID]=tcp:5432",
            "-credential_file=/secrets/cloudsql/credentials.json",
          ]
        volumeMounts:
          - name: cloudsql-oauth-credentials
            mountPath: /secrets/cloudsql
            readOnly: true
          - name: ssl-certs
            mountPath: /etc/ssl/certs
          - name: cloudsql
            mountPath: /cloudsql
      volumes:
        - name: cloudsql-oauth-credentials
          secret:
            secretName: cloudsql-oauth-credentials
        - name: ssl-certs
          hostPath:
            path: /etc/ssl/certs
        - name: cloudsql
          emptyDir:

```

##### Django

`/api/healthz`へのリクエストに対してHTTP200を返すように変更します。

```python:todo/urls.py
# todo/urls.py
from django.urls import path, include
from .views import ListTodo, DetailTodo, health_check

urlpatterns = [
    path('<int:pk>/', DetailTodo.as_view()),
    path('', ListTodo.as_view()),
    path('healthz', health_check, name="healthz")  # 追加
]
```

```python:todo/views.py
# todos/views.py

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from .models import Todo
from .serializers import TodoSerializer

def health_check(request):
    response = HttpResponse(status=200)
    return response

class ListTodo(generics.ListAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer


class DetailTodo(generics.RetrieveAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
```

##### 更新

```sh
# Ingressの更新
\gke-django-tutorial\kubectl apply -f ingress.yml
ingress.extensions/ingress-service created

# 確認
\gke-django-tutorial\kubectl get ingress
NAME              HOSTS   ADDRESS        PORTS   AGE
ingress-service   *       34.95.105.61   80      112s
```

また、コンソール上から`Compute Engine > ヘルスチェック`を確認すると、Serviceに対するヘルスチェック先のパス一覧が表示されます。

backendサービスのポートと一致する使用リソースのパスを`/api/healthz`に変更しておきましょう。

#### 静的IPアドレスで公開する

現在のIngressの`ADDRESS`はエファメラルIPアドレスなので、静的IPアドレスを予約してIngressが予約したIPアドレスを使用するようにIngressリソースを構成します。

```sh
# 静的IPアドレスの予約
\gke-django-tutorial\gcloud compute addresses create [STATIC_IP_ADDRESS] --global
Created [https://www.googleapis.com/compute/v1/projects/[YOUT_PROJECT]/global/addresses/[STATIC_IP_ADDRESS]].
```

```yml:ingress.yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-service
  namespace: default
  annotations:  # 追加
    kubernetes.io/ingress.class: gce
    kubernetes.io/ingress.global-static-ip-name: [STATIC_IP_ADDRESS]  # 追加

spec:
  rules:
    - http:
# [省略]
```

```sh
# ingressの更新
\gke-django-tutorial\kubectl apply -f ingress.yml

# 静的IPアドレスの確認
\gke-django-tutorial\gcloud get ingress
NAME              HOSTS   ADDRESS          PORTS   AGE
ingress-service   *       12.345.678.910   80      40m

# 確認
\gke-django-tutorial\curl http://12.345.678.910/api/
[{"id":1,"title":"title1","body":"body1"},{"id":2,"title":"title2","body":"body2"},{"id":3,"title":"title3","body":"body3"}]
```

確かにAPIが機能していることを確認しました。また、コンソールからも`VPCネットワーク > 外部IPアドレス`を確認すると、取得した静的IPアドレスと名前が確認できます。

### ドメインの取得

Ingressで公開している静的IPアドレスとDNSレコードを構成してドメイン名でアクセスできるようにしていきます。

#### Google Domains

Google Domainsでドメインを取得します。`新しいドメインを取得`から取得したいドメイン名を入力して購入します。

#### Cloud DNS

[Cloud DNS クイックスタート](https://cloud.google.com/dns/docs/quickstart?hl=ja#create_a_new_record)に従い
新しいレコードを作成して、ドメインを外部IPアドレスにポイントします。

コンソールの`ネットワークサービス > Cloud DNS`にて`DNSゾーン`を作成します。

```
ゾーンのタイプ: 公開
ゾーン名: [DNS_ZONE]
DNS名: domain.page(取得したドメイン)
DNSSEC: オフ
```

Aレコードセットを追加します。

```
DNS名: (入力なし).domain.page
リソースレコードのタイプ: A
TTL: 5
IPv4アドレス: 12.345.678.910
```

CNAMEレコードの作成をします。

```
DNS名: www.domain.page
リソースレコードのタイプ: CNAME
TTL: 5
正規名: domain.page.
```

#### ドメインのネームサーバーを更新する

NSレコードにある4つのDNSサーバーをGoogle Domainsのネームサーバーに登録します。

参考:
- [Google Cloud DNSでIPアドレスとドメイン名を紐付ける](https://qiita.com/NagaokaKenichi/items/95052742d40392f3215e)

DNSの設定が反映されたらAPIが返ってくるか動作確認をしみましょう。

```sh
\gke-django-tutorial\curl http://domain.page/api/
```

#### Ingressにホストを反映する

ingressの宣言ファイルにホスト名を追加します。
ingress.ymlを下記のように更新します。

```yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-service
  namespace: default
  annotations:
    kubernetes.io/ingress.class: gce
    kubernetes.io/ingress.global-static-ip-name: [STATIC_IP_NAME]
spec:
  rules:
  - host: domain.page  # 追加
    http:
      paths:
      - path: /*
        backend:
          serviceName: frontend-node-service
          servicePort: 3000
      - path: /api/*
        backend:
          serviceName: backend-node-service
          servicePort: 8000
      - path: /admin/*
        backend:
          serviceName: backend-node-service
          servicePort: 8000

```

ingress.ymlを変更したので更新します。

```sh
$\gke-django-tutorial\kubectl apply -f ingress.yml
```

### HTTPS化

GoogleマネージドSSL証明書を構成してHTTPS化します。これには`ManagedCertificate`オブジェクトを作成します。

参考:
- [Google マネージド SSL 証明書の使用](https://cloud.google.com/kubernetes-engine/docs/how-to/managed-certs?hl=ja)

```yml
apiVersion: networking.gke.io/v1beta1
kind: ManagedCertificate
metadata:
  name: domain-certificate
spec:
  domains:
    - domain.page
```

```sh
$ kubectl apply -f vertificate.yml
```

HTTPへのリクエストがHTTPSにリダイレクトされるようにIngressのannotationを更新します。

```yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-service
  namespace: default
  annotations:
    kubernetes.io/ingress.class: gce
    kubernetes.io/ingress.global-static-ip-name: [STATIC_IP_NAME]
    kubernetes.io/ingress.allow-http: "false"  # HTTPSのみ受け付ける
    networking.gke.io/managed-certificates: domain-certificate  # 使用したManagedCertificate
# ...[省略]
```

```sh
$ kubectl apply -f ingress.yml
```

これで`https://domain.page/`にアクセスするとHTTPSができていることを確認できます。
が、しかし画面には何も現れません。frontendのTodoを取得するエンドポイントは`http://localhost:8000/api/`のままになっているためです。

### コンテナのロールアウト

kubernetesでは古いポッドの停止と新しいポッドへの起動を繰り返してサービスをアップデートすることができます。
今回はfrontendとbackendのコンテナを更新してきちんと機能することを確認します。
コンテナの更新はコンテナのラベルを新しく指定することで新しいコンテナに適用することができます。
コンテナのラベルはなにも考えずに`latest`としてDeploymentをデプロイしてきましたが、ラベルを使って使用するコンテナを指定することができます。
今回は`v1.0`としてコンテナをロールアウトしてみたいと思います。

#### frontend

`frontend\src\App.js`でデータを取得するリクエスト先を`https://sawakome.page/api/`に変更します。

```javascript
import React, { Component } from 'react';
import axios from "axios";
import './App.css';

class App extends Component {
  state = {
    todo: []
  };

  componentDidMount() {
    this.getTodos();
  }

  getTodos() {
    axios
      .get("https://domain.page/api/")  // 変更
      .then(res => {
        this.setState({ todo: res.data });
      })
      .catch(err => {
        console.log(err);
      });
  }
  render() {
    return (
      <div>
        {this.state.todo.map(item => (
          <div key={item.id}>
            <h1>{item.title}</h1>
            <p>{item.body}</p>
          </div>
        ))}
      </div>
    );
  }
}

export default App;

```

#### backend

`backend\config\settings.py`の`CORS_ORIGIN_WHITELIST`に取得したドメインを追加します。

```python:settings.py

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000','https://domain.page',
)
```

#### コンテナイメージのビルド

backend, frontendのDeploymentでは使用するコンテナを
- `image: gcr.io/gke-django-tutorial/frontend:v1.0`
- `image: gcr.io/gke-django-tutorial/backend:v1.0`
のように書き換えてデプロイし直します。

```sh
# イメージのビルド
$\gke-django-tutorial\docker image build --no-cache -t gcr.io/gke-django-tutorial/backend:v1.0 ./backend

$\gke-django-tutorial\docker image build --no-cache -t gcr.io/gke-django-tutorial/frontend:v1.0 ./frontend

# イメージをGCRにアップロードする
$\gke-django-tutorial\gcloud docker -- push gcr.io/gke-django-tutorial/backend:v1.0

$\gke-django-tutorial\gcloud docker -- push gcr.io/gke-django-tutorial/frontend:v1.0

# デプロイメントを更新する
$\gke-django-tutorial\kubectl apply -f backend-deployment.yml

$\gke-django-tutorial\kubectl apply -f frontend-deployment.yml
```

参考:
- [コンテナ化されたウェブ アプリケーションのデプロイ](https://cloud.google.com/kubernetes-engine/docs/tutorials/hello-app)

これで`https://domain.page/`にアクセスするとfrontendのTodoアイテムが表示されました。
また、`https://domain.page/admin/`にアクセスするとbackendのDjangoの管理者画面に飛ぶことが確認できました。Ingressによるルーティングが機能していることがわかります。

## CloudStorageのCORSの構成

`https:domain.page/admin/`のCSSが反映されていない、もしくは開発者ツールを確認すると
`Cloud Storage has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.`というエラーが発生している場合には
バケットの[クロスオリジンリソースシェアリング(CORS)の構成](https://cloud.google.com/storage/docs/configuring-cors#gsutil)を設定しましょう。

CORSの構成は構成を記述したjsonファイルをgsutilを使って追加することができます。

```sh
# バケットのCORSを確認
$\gke-django-tutorial\gsutil cors get gs://[STORAGE_NAME]

# 構成ファイルの作成
$\gke-django-tutorial\type nul > cors-json-file.json
```

jsonファイルを作成します。

```json
[
  {
    "origin": ["https://domain.page"],
    "responseHeader": ["Content-Type"],
    "method": ["GET", "HEAD", "DELETE"],
    "maxAgeSeconds": 3600
  }
]
```

jsonを使ってCORSを追加します。

```sh
$\gke-django-tutorial\gsutil cors set cors-json-file.json gs://[STORAGE_NAME]
```

## お掃除

プロジェクトを削除すれば全て消えます。
プロジェクトは残してクラスタだけ削除する場合、予約した静的IPアドレスは削除されません。
下記コマンドで削除してください。

```sh
# 静的IPアドレスの削除
gcloud compute addresses delete [STATIC_IP_NAME] --global
```

## つまづいたところ

KubernetesのキャッチアップとGKEにデプロイしたときにどういう挙動をしているのかを把握していくのに時間がかかってしまいました。
GAEの手軽さが恋しいです。

- ヘルスチェックの存在
    ヘルスチェックの存在を知らずローカルで`docker-compose up`すれば動作するのにGKEにデプロイすると起動せず困りました。
    Podへはヘルスチェックへのパスを通すことが大切ですね。。

- frontendのエンドポイントはどこ？
    Pod内のコンテナ間はDjangoとcloud_sql_proxyのように`localhost:PORT`で通信できるので,frontendからbackendも同じように
    通信できるはずだと思い込んでいました。frontendはクライアントのブラウザで実行されるのに`localhost`で解決できるはずないですね。。

- Kubernetesのリソースの種類
    DeploymentとServiceとIngressが何を意味しているのか、最初はまったくわかりませんでした。
    特にServiceでもタイプによっては外部公開できるのでIngressとServiceの何が違うのか理解するのに時間がかかりました。。
    公式のGKEにDjangoをデプロイする[チュートリアル](https://cloud.google.com/python/django/kubernetes-engine)ではLoadBalancerタイプのServiceの使って公開していて
    これをIngress化するように進めていきました。

## まだできないこと

- CI/CDの構築もするべきだった
    frontendのエンドポイントの指定の方法につまづいたとき、`コード修正⇒イメージ作成⇒Push⇒更新`のサイクルが本当に面倒なのでCI/CDは最初にやるべきでした。
    そのうち記事を書きたいと考えています。

- マネージドなSSLから複数TLS証明書の利用
    正直この辺の仕組みを浅くしか理解できておらず、チュートリアルに沿って「とりあえず対応した」という形なので
    複数ドメインをIngressで捌く、みたいな形には適用できていません。セキュリティ面へのキャッチアップがまだまだ薄いです。。

- ヘルスチェックとNginx
    backendのDjangoですが、`ALLOWED_HOST`が`ALLOWED_HOST = [*]`のままになっていてこのまま公開するのは[危険です](https://docs.djangoproject.com/ja/3.0/ref/settings/#allowed-hosts)。
    `ALLOWED_HOST = ["ドメイン名"]`のようにドメインに絞りたかったのですが、これをするとマスターノードからのヘルスチェックが通らなくなってしまい、
    backendが機能しなくなってしまいました。
    これはPodにリバースプロキシとしてNginxコンテナを追加してヘルスチェックはNginxがレスポンスを返して、アプリケーションへのリクエストはNginxがDjangoに通す形にすれば
    Django側は`ALLOWED_HOST = ["ドメイン名"]`で済むわけです。ただNginxのキャッチアップがまだ追いついてないです。。


