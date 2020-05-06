# ゼロからGKEにDjango+Reactをデプロイする(1)backendの開発 - Nginx + Django

## やりたいこと

Djagno+Reactの構成でアプリケーションを開発してGoogle Kubernetes Engineにデプロイしたいけれどもまとまったチュートリアルが有りそうで無かったので書きました。

ただ**まだ完全ではない点があると思います**が、少し経験がある方ならすぐに利用できるんじゃないかと思っています。

## 注意

これは未経験の趣味エンジニアがポートフォリオを作成するためにデプロイと格闘した記録です。
不備があれば何卒御指摘をお願い致します。。

## 目指す姿

![architecture.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/224317/e24509e1-5c08-ae2b-76a7-12a9642f45cd.png)

## 環境

``` sh
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

``` sh
# プロジェクトフォルダの作成
$ mkdir gke-django-tutorial
$ cd gke-django-tutorial

# ディレクトリを作成する
$\gke-django-tutorial\mkdir backend
$\gke-django-tutorial\mkdir frontend
```

### backendの開発(Djagno編)

backendのPodはDjango-rest-frameworkでRestAPIを配信します。
backendのPod内について整理しておきます。

| 役割            | コンテナイメージ                          |
|-----------------|-----------------------------------|
| プロキシサーバー        | Nginx:1.17.4-alpine               |
| アプリケーション        | Python3.7 - Django rest framework |
| cloud_sql_proxy | gcr.io/cloudsql-docker/gce-proxy  |

backend内のディレクトリを作成します。

``` sh
# backendディレクトリに移動
$\gke-django-tutorial\cd backend

# djangoディレクトリの作成
$\gke-django-tutorial\backend\mkdir web-back

# Nginxディレクトリの作成
$\gke-django-tutorial\backend\mkdir nginx
```

#### Djangoでプロジェクトを始める

Pythonの仮想環境を作成してDjangoでAPIサーバーを開発していきます。
これは `backend\web-back\` ディレクトリ内に作成します。

``` sh
# web-backディレクトリ
$\gke-django-tutorial\backend\cd web-back

# Pythonの仮想環境作成
$\gke-django-tutorial\backend\web-back\python -m venv venv

# 仮想環境の有効化
$\gke-django-tutorial\backend\web-back\venv\Scripts\activate

# Pythonパッケージのインストール
(venv)$\gke-django-tutorial\backend\web-back\python -m install --upgrade pip setuptools
(venv)$\gke-django-tutorial\backend\web-back\python -m install django djangorestframework python-dotenv

# Djangoのプロジェクトを始める
(venv)$\gke-django-tutorial\backend\web-back\django-admin startproject config .
```

web-backディレクトリ下で `django-admin startprject config .` とすることで
`config` というDjangoプロジェクトフォルダが作成されました。

ローカルサーバーが起動するかどうか確認しましょう。

``` sh
(venv)$\gke-django-tutorial\backend\web-back\python manage.py runserver
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

開発用サーバーが起動したので `http://localhost:8000/` にアクセスすると `The install worked successfully!` の画面が確認できます。

#### settings.py

`config/settings.py` を編集して基本的な設定を盛り込みます。
`settings.py` の秘匿すべき情報は `.env` ファイルに記述して公開しないようにします。
python-dotenvパッケージを使って `.env` に記載された情報を利用するように変更しましょう。

``` sh
# .envファイルの作成
(venv)$\gke-django-tutorial\backend\web-back\type nul > .env
```

``` python
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
(venv)$\gke-django-tutorial\backend\web-back\python manage.py startapp todo
```

`config/settings.py` の `INSTALLED_APPS` に `todo` と `rest_framework` を追加します。

``` python
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

`rest_framework.permissions.AllowAny` はdjango-rest-frameworkが暗黙的に決めているデフォルトの設定 `'DEFAULT_PERMISSION_CLASSES'` を解除するためのものです。

#### todo/models.py

`todo` アプリケーションmodelを作成します。

``` python
# todo/models.py
from django.db import models

class Todo(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return self.title

```

`todo/admin.py` に作成したモデルを追加します。

``` python
# todo/admin.py
from django.contrib import admin
from .models import Todo

admin.site.register(Todo)
```

マイグレーションします。

``` sh
(venv)$\gke-django-tutorial\backend\web-back\python manage.py makemigrations
Migrations for 'todo':
  todo\migrations\0001_initial.py

    - Create model Todo

(venv)$\gke-django-tutorial\backend\web-back\python manage.py migrate
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

``` sh
(venv)$\gke-django-tutorial\backend\web-back\python manage.py createsuperuser
ユーザー名 (leave blank to use '[YOUR_NAME]'): [USER_NAME]
メールアドレス: YOUR_MAIL_ADDRESS@MAIL.COM
Password:
Password (again):
Superuser created successfully.
```

開発用サーバーを起動して `http://localhost:8000/admin/` にアクセスするとDjango管理サイトログイン画面が表示されます。設定したユーザー名、パスワードを入力してログインしてみましょう。

ログインできると作成したアプリケーション `Todo` のテーブルを確認することができます。
2，3個アイテムを追加しておきましょう。

#### URLs

`config/urls.py` にtodoアプリケーソンへのルーティングを追加します。

``` python
# config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('todo.urls'))  # 追加
]

```

#### todo/urls.py

`todo/urls.py` を作成します。

``` sh
(venv)$\gke-django-tutorial\backend\web-back\type nul > todo\urls.py
```

``` python
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

``` sh
(venv)$\gke-django-tutorial\backend\type nul > todo\serializers.py
```

``` python
# todo/serializers.py
from rest_framework import serializers
from .models import Todo

class TodoSerializer(serizers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ('id', 'title', 'body')

```

`fields = ('id', 'title', 'text')` での `id` はmodelにて `PrimaryKey` を指定しない場合、Django によって自動的に追加されます。

#### todo/views.py

Django rest frameworkで `views.py` を作成する場合は `rest_framework.generics` の `~~APIView` を継承します。

``` python
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

routerなど設定できていませんが、とりあえずはTodoアプリケーションのアイテムをRest APIとして配信できる準備ができました。
開発サーバーで `http://127.0.0.1:8000/api/` にアクセスするとAPIviewを確認することができます。

ここまではDjangoでよくあるローカル環境での開発です。

#### CORS

Django( `localhost:8000` )がReact( `localhost:3000` )とjson のやり取りをするには
CORS(Cross-Origin Resource Sharing)の設定を行う必要があります。

`django-cors-headers` をインストールしましょう。

``` sh
(venv)$\gke-django-tutorial\backend\web-back\python -m pip install django-cors-headers
```

`config/settings.py` を更新します。

``` python
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

`config/settings.py` は本番環境に使用することを考慮し、 `config/local_settings.py` を作成してローカル開発用に分けておきます。
GKEデプロイ時にはCloudSQLを使用し、ローカルではsqlite3を使用するように、settings.pyを分けておくことで設定値を書き換えずに済みます。

``` sh
# ファイルの作成
(venv)$\gke-django-tutorial\backend\web-back\type nul > config/local_settings.py
```

``` python
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

`config/local_settings.py` を使って開発用サーバーを起動しておきます。

``` sh
(venv)$\gke-django-tutorial\backend\web-back\python manage.py runserver --settings config.local_settings
```

#### Tests

テストを書きます。

``` python
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

``` sh
(venv)$\gke-django-tutorial\backend\web-back\python manage.py test
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
配信用の静的ファイルを集約するディレクトリは `staticfiles/` とし、開発用に追加する静的ファイルディレクトリは `static/` としています。

``` sh
# 静的ファイル配信用ディレクトリ
(venv)$\gke-django-tutorial\backend\web-back\mkdir staticfiles

# 静的ファイル開発用ディレクトリ
(venv)$\gke-django-tutorial\backend\web-back\mkdir static

# 静的ファイルの集約
(venv)$\gke-django-tutorial\backend\web-back\python manage.py collectstatic
```

`staticfiles/` ディレクトリ下にadminのCSSなども追加されるのが確認できます。

#### Pythonパッケージの追加

GKEにデプロイする際にはCloud SQLのPostgresを利用します。
DjangoからPostgresを使用するにはpsycopig2が必要です。
また、アプリケーションの起動にはgunicornを使用します。

必要なパッケージを追加でインストールし、仮想環境にインストールしたPythonパッケージをrequirements.txtにまとめておきます。

``` sh
# パッケージのインストール
(venv)$\gke-django-tutorial\backend\web-back\python -m pip install wheel gunicorn psycopg2-binary

# requirements.txtの更新
(venv)$\gke-django-tutorial\backend\web-back\python -m pip freeze > requirements.txt
```

実行するとbackend/下にrequirements.txtが作成されます。

``` txt
asgiref==3.2.7
Django==3.0.5
django-cors-headers==3.2.1
djangorestframework==3.11.0
gunicorn==20.0.4
psycopg2-binary==2.8.5
python-dotenv==0.13.0
pytz==2019.3
sqlparse==0.3.1
```

#### Dockerfileの作成

Django側のコンテナイメージを作成するためのDockerfileを作成します。

``` sh
# Dockerfileの作成
(venv)$\gke-django-tutorial\backend\web-back\type nul > Dockerfile

# .dockerignoreの作成
(venv)$\gke-django-tutorial\backend\web-back\type nul > .dockerignore
```

``` Dockerfile
# backend/web-back/Dockerfile

# set base image
FROM python:3.7

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /code

# install dependencies
COPY requirements.txt ./
RUN python3 -m pip install --upgrade pip setuptools
RUN pip install -r requirements.txt

# Copy project
COPY . ./

# Expose application port
EXPOSE 8000
```

.dockerignoreも作成してコンテナ内に入れたくないファイルを分けておきます。

```.dockerignore
venv/
.env
Dockerfile
config/local_settings.py

``` 

これでDjangoに関するDockerイメージを作成する準備ができました。

### backendの開発(Nginx編)

backend-Pod内のリバースプロキシサーバーとしてNginxコンテナを配置します。
Nginxは `/etc/nginx/conf.d/` 内の設定ファイルを使ってリバースプロキシの機能を定義していきます。

また、backendの開発編の最後にはdocker-composeで起動させてみたいと思うので、docker-compose用のファイルも作成しておきます。

```sh
# Nginx用のファイル作成
$\gke-django-tutorial\backened\nginx\type nul > Dockerfile
$\gke-django-tutorial\backened\nginx\type nul > Dockerfile.dev
$\gke-django-tutorial\backened\nginx\type nul > default.conf
$\gke-django-tutorial\backened\nginx\type nul > default.dev.conf
```

`default.conf` は `Nginxコンテナ:80` ⇒ `Django:8000` となるようにリバースプロキシを設定しました。

`location = /healthz` ディレクティブはGKEにデプロイ後に必要になるヘルスチェック用のパスです。
`location /static/` ディレクティブは静的ファイルを配信するためのパスです。これが無いと管理者画面のCSSが適用されません。GKEにデプロイ時には静的ファイルはCloud Storageから配信するようにするので、削除します。

`server` ディレクティブはGKEにデプロイする場合は `localhost:8000` とし、docker-composeで起動する場合は `web-back:8000` としています。
これはdocker-composeで起動する場合はサービス名で名前解決をする必要があるためです。GKEにデプロイする場合は同じPod内にあるため、 `localhost:8000` で名前解決可能です。

``` conf
; default.dev.conf
upstream django {
    server web-back:8000;
}

; default.confの場合
; upstream django {
    ; server localhost:8000;
; }

server {

    listen 80;

    location = /healthz {
        return 200;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect off;
    }

; GKEデプロイ時には削除
    location /static/ {
        alias /code/staticfiles/;
    }
}

```

DockerfileはNginxの設定ファイルをNginxコンテナにコピーさせることで設定を反映させます。

``` Dockerfile
# backend\nginx\Dockerfile.dev
FROM nginx:1.17.4-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY default.dev.conf /etc/nginx/conf.d

# backend\nginx\Dockerfile.devの場合
# COPY default.conf /etc/nginx/conf.d

```

### backendの開発(docker-compose編)

docker-composeを使ってNginx+Djangoの構成でコンテナを起動させたいと思います。

``` sh
# docker-compose.ymlの作成
$\gke-django-tutorial\backend\type nul > docker-compose.yml
```

``` yml
version: "3.7"

services:
  web-back:
    container_name: python-backend
    env_file: ./web-back/.env
    build: ./web-back/.
    volumes:

      - ./web-back:/code/
      - static_volume:/code/staticfiles # <-- bind the static volume

    stdin_open: true
    tty: true
    command: gunicorn --bind :8000 config.wsgi:application
    networks:

      - backend_network

    environment:

      - CHOKIDAR_USEPOLLING=true
      - DJANGO_SETTINGS_MODULE=config.local_settings

  server:
    container_name: nginx
    build:
      context: ./nginx/.
      dockerfile: Dockerfile.dev
    volumes:

      - static_volume:/code/staticfiles # <-- bind the static volume

    ports:

      - "8080:80"

    depends_on:

      - web-back

    networks:

      - backend_network

networks:
  backend_network:
    driver: bridge
volumes:
  static_volume:
```

``` sh
# docker-compose.ymlで起動する
$\gke-django-tutorial\backend\docker-compose up --build
```

`http://localhost:8080` ⇒ `Nginxコンテナ:80` ⇒ `Django:8000` となるように
ポートフォワーディングされています。

`http://localhost:8080/admin/` にアクセスしてCSSが反映されているかどうかを確認しましょう。

ローカル環境下でdocker-composeで起動してbackendの開発ができる環境が整いました。

⇒[(2)frontendの開発: Nginx + React]()へ
