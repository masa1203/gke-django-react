# ゼロからGKEにDjango+Reactをデプロイする(7)静的IPとドメイン取得

[(6)serviceとIngress](https://qiita.com/komedaoic/items/0f4c5366fc490aaf47dc)の続きです。

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

### 静的IPアドレスで公開する

現在のIngressの `ADDRESS` はエファメラルIPアドレスなので、静的IPアドレスを予約してIngressが予約したIPアドレスを使用するようにIngressリソースを構成します。

``` sh
# 静的IPアドレスの予約
\gke-django-tutorial\gcloud compute addresses create [STATIC_IP_ADDRESS_ID] --global
Created [https://www.googleapis.com/compute/v1/projects/[YOUT_PROJECT]/global/addresses/[STATIC_IP_ADDRESS_ID]].
```

```yml:ingress.yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-service
  namespace: default
  annotations:  # 追加

    kubernetes.io/ingress.class: gce
    kubernetes.io/ingress.global-static-ip-name: [STATIC_IP_ADDRESS_ID]  # 追加

spec:
  rules:

    - http:

# [省略]

``` 

```sh
# ingressの更新
\gke-django-tutorial\manifests\kubectl apply -f ingress.yml

# 静的IPアドレスの確認
\gke-django-tutorial\gcloud get ingress
NAME              HOSTS   ADDRESS          PORTS   AGE
ingress-service   *       12.345.678.910   80      40m

# 確認
\gke-django-tutorial\curl http://12.345.678.910/api/
[{"id":1,"title":"title1","body":"body1"},{"id":2,"title":"title2","body":"body2"},{"id":3,"title":"title3","body":"body3"}]
```

取得した静的IPアドレスから返答があり、確かにAPIが機能していることが確認できました。
また、コンソールからも `VPCネットワーク > 外部IPアドレス` を確認すると、取得した静的IPアドレスと名前が確認できます。

### ドメインの取得

Ingressで公開している静的IPアドレスとDNSレコードを構成してドメイン名でアクセスできるようにしていきます。

#### Google Domains

Google Domainsでドメインを取得します。 `新しいドメインを取得` から取得したいドメイン名を入力して購入します。

#### Cloud DNS

[Cloud DNS クイックスタート](https://cloud.google.com/dns/docs/quickstart?hl=ja#create_a_new_record)に従い
新しいレコードを作成して、ドメインを外部IPアドレスにポイントします。

コンソールの `ネットワークサービス > Cloud DNS` にて `DNSゾーン` を作成します。
ここでは取得したドメインを仮に `domain.page` とし、紐づくIPアドレスは `12.345.678.910` としています。

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

* 参考:
    - [Google Cloud DNSでIPアドレスとドメイン名を紐付ける](https://qiita.com/NagaokaKenichi/items/95052742d40392f3215e)

DNSの設定が反映されたらAPIが返ってくるか動作確認をしみましょう。

``` sh
$\gke-django-tutorial\curl http://domain.page/api/
```

#### Ingressにホストを反映する

ingressの宣言ファイルにホスト名を追加します。
ingress.ymlを下記のように更新します。

``` yml
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

  + host: domain.page  # 追加

    http:
      paths:

      - path: /*

        backend:
          serviceName: frontend-node-service
          servicePort: 80

      - path: /api/*

        backend:
          serviceName: backend-node-service
          servicePort: 80

      - path: /admin/*

        backend:
          serviceName: backend-node-service
          servicePort: 80

```

ingress.ymlを変更したので更新します。

``` sh
$\gke-django-tutorial\manifests\kubectl apply -f ingress.yml
```

取得した静的IPとドメインを使って公開できる準備が完了しました。

⇒[(8)HTTPS化とロールアウト]()
