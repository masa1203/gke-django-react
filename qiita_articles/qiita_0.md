# ゼロからGKEにDjango+Reactをデプロイする: 目次

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

## 目次

* [(1)backendの開発: Nginx + Django](https://qiita.com/komedaoic/items/8626b52070163290d8f1)
* [(2)frontendの開発: Nginx + React](https://qiita.com/komedaoic/items/777cc8db007be748a828)
* [(3)GCPのプロジェクトを作成する](https://qiita.com/komedaoic/items/45a0082467c6b290622d)
* [(4)クラスタの作成とコンテナPUSH](https://qiita.com/komedaoic/items/99b5afb169bc5b37472a)
* [(5)Deployment](https://qiita.com/komedaoic/items/6f194cc59665f6af4749)
* [(6)ServiceとIngress](https://qiita.com/komedaoic/items/0f4c5366fc490aaf47dc)
* [(7)静的IPとドメイン取得](https://qiita.com/komedaoic/items/c998180c66c6919c9f40)
* [(8)HTTPS化とロールアウト](https://qiita.com/komedaoic/items/10199b1f65133936f728)
* [(9)掃除とまとめ](https://qiita.com/komedaoic/items/61750ac97059f19c3ea3)
