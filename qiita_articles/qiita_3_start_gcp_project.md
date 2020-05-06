# ゼロからGKEにDjango+Reactをデプロイする(3)GCPのプロジェクトを作成する

[(2)frontendの開発 - Nginx + React]()の続きです。

## やりたいこと

Djagno+Reactの構成でアプリケーションを開発してGoogle Kubernetes Engineにデプロイしたいけれども
まとまったチュートリアルが有りそうで無かったので書きました。

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

## デプロイ

Google Kubernetes Engine(以下、GKE)にデプロイしていきます。
[公式チュートリアル](https://cloud.google.com/python/django/kubernetes-engine)を大いに参考にしています。

### GCPのプロジェクトを作成

GoogleアカウントにログインしてCloudコンソールから新しいプロジェクトを開始します。

プロジェクト名: gke-django-tutorial
場所: 組織なし

### 課金が有効かどうかを確認する

参考 : https://cloud.google.com/billing/docs/how-to/modify-project?authuser=2

### Cloud SDKを初期化

GCPのリソースはローカルPCからCloud SDKを使って操作することができます。
gcloudは既にインストールしてある想定です。

``` sh
# gcloudの初期化
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

[以下省略]

```

### 必要なAPIを有効にする

Datastore, Pub/Sub, Cloud Storage JSON, Cloud Logging, and Google+APIs を有効にします。

### CloudSQLの準備

#### Cloud SQL Adminを有効にする

``` sh
$\gke-django-tutorial\gcloud services enable sqladmin
Operation "operations/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" finished successfully.
```

#### CloudSQL proxyのダウンロード

Cloud SQL Proxyをダウンロードして `cloud_sql_proxy.exe` に名前を変更します。
これは `$\gke-django-tutorial\` 下に設置しました。

* 参考: [Installing the Cloud SQL Proxy](https://cloud.google.com/python/django/kubernetes-engine#installingthecloudsqlproxy)

#### CloudSQL インスタンスの作成

CloudコンソールからCloudSQLのインスタンスを作成します。

``` sh
データベースエンジンの選択: PostgreSQL
インスタンスID: [SQL_INSTANCE_NAME]
パスワード: [YOUR_PASSWORD]
ロケーション:
    リージョン: [SQL_REGION_NAME]
    ゾーン: [DATABASE_ZONE]
データベースのバージョン: PostgreSQL 11
```

#### インスタンスの初期化

先ほどダウンロードした `cloud_sql_proxy.exe` を使ってCloudSQLに接続するための `connectionName` を確認します。

``` sh
# connecsionNameの確認
$\gke-django-tutorial\gcloud sql instances describe [SQL_INSTANCE_NAME]
connectionName: [YOUR_PROJECT]:[SQL_REGION_NAME]:[SQL_INSTANCE_NAME]

# インスタンスの接続
$\gke-django-tutorial\gcoud_sql_proxy.exe -instances="[YOUR_PROJECT]:[SQL_REGION_NAME]:[SQL_INSTANCE_NAME]"=tcp:5432
2020/04/28 17:49:51 Listening on 127.0.0.1:5432 for gke-django-tutorial:asia-northeast1:websql
2020/04/28 17:49:51 Ready for new connections
```

このコマンドによって手元のPCからCloudSQLインスタンスに接続することができました。
インスタンスに接続したコマンドプロンプトはそのままにして、別のコマンドプロントで作業します。

#### データベースの作成

コンソールからデータベースを作成しましょう。コンソール上の `[SQL_INSTANCE_NAME]` を選択して `データベース` から `データベースを作成` することができます。

``` sh
データベース名: [DATABASE_NAME]
```

#### データベースユーザーの作成

コンソールからデータベースのユーザーアカウントを作成しておきます。

``` sh
ユーザー名: [DATABASE_USER]
パスワード: [DATABASE_PASSWORD]
```

#### CloudSQLのサービスアカウントの作成

コンソールからCloudSQlのサービスアカウントを作成して、json形式のプライベートキーをダウンロードしましょう。

``` sh
サービスアカウント名: [SERVICE_ACCOUNT_NAME]
サービスアカウントID: [SERVICE_ACCOUNT_NAME]@BBBBBBBBB.iam.gservice
権限: Cloud SQL 管理者
⇒プライベートキーの作成でjson形式を選択
⇒json形式のプライベートキー: ZZZZZZZZZZZZZZZ.jsonがダウンロードされる
```

プロジェクト直下に `secrets\cloudsql\` というディレクトリを作成して作成したプライベートキーを設置します。

``` sh
$\gke-django-tutorial\mkdir secrets
$\gke-django-tutorial\cd secrets
$\gke-django-tutorial\secrets\mkdir cloudsql
$\gke-django-tutorial\secrets\cd cloudsql

# プライベートキーのしておく
$\gke-django-tutorial\secrets\cloudsql\dir
ZZZZZZZZZZZZZZZ.json
```

#### 環境変数の設定

DjangoのデータベースをCloudSQLに設定して起動し、CloudSQLを利用する準備をしていきます。
ローカルのsqlite3でも行ったように、テーブルのマイグレーションをローカル環境からcloud_sql_proxyを通して行っていきます。

`DATABASE_USER` と `DATABASE_PASSWORD` を環境変数として利用するため、 `.env` ファイルに追加します。
keyとvalueの間にスペースを置かないようにしましょう。

``` sh
SECRET_KEY='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
DEBUG=False
DATABASE_USER=[DATABASE_USER]
DATABASE_PASSWORD=[DATABASE_PASSWORD]
```

#### backend/config/settings.py

DjangoのDATABASE設定をdb.sqlite3からCloudSQLに変更します。
`.env` ファイルを直接参照する必要があるため、 `python-dotenv` を使って読み込みます。

``` python
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

データベースの設定をCloudSQLに変更したのでマイグレーションし直す必要があります。

``` sh
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

``` sh
(venv)$\gke-django-tutorial\backend\python manage.py createsuperuser
ユーザー名 (leave blank to use '[YOUR_NAME]'): [SUPERUSER_NAME]
メールアドレス: [YOUR_EMAIL]@gmail.com
Password:
Password (again):
Superuser created successfully.
```

開発用サーバーを立ち上げて管理者ページからデータを3つほど追加しておきましょう。

``` sh
(venv)$\gke-django-tutorial\backend\python manage.py runserver
```

`http://localhost:8000/admin/` で管理者ページにログインすると、CloudSQLインスタンスに作成したデータベース上にデータを格納することができます。
2，3個アイテムを追加しておきましょう。

### Cloud Storageの準備

静的ファイルをGoogle Cloud Storage(以下、GCS)に格納して、静的ファイルはGCSから配信するための設定を行います。

ストレージを作成して静的ファイルをアップロードします。これをしないとadmin画面などのcssが反映されません。

``` sh
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

`backend/config/settings.py` の `STATIC_URL` をGCSを参照するように変更します。

``` python
# backend/config/settings.py
STATIC_URL = 'https://storage.googleapis.com/[STORAGE_NAME]/static/'
```

⇒[(4)クラスタの作成とコンテナPUSH]()へ
