# nameless_bot
現時点では非公開なDiscordサーバーで稼働することを目的に書かれたDiscord BOTのソースです。

パッケージはpipenvで管理しています。

# contribute
もし参加したい方がいればDiscordでお知らせください。

## 環境構築
ローカル環境で開発する場合は、pipenvのインストールと、リモートリポジトリの接続が必要です。

```
$ pip install pipenv
```

で pipenv をインストールし、リポジトリを保管するフォルダ(ディレクトリ)を作成します。
ここではフォルダ名を「folder」とします。

`cd` コマンドで folder ディレクトリに移動し、

```
$ git init
$ git remote add origin https://github.com/coolwind0202/nameless_bot.git
$ git pull origin main
```

でリモートリポジトリをローカルへコピーします。

```
$ pipenv --python 3
```

を実行しPython3で環境を初期化します。

```
$ pipenv shell
```

を実行し、 folder 下でpipenvを有効化します。

```
$ pipenv install
```

で、依存しているパッケージのインストールが完了します。

## コミット
変更が完了したら以下の作業を行います。

```
$ git add .
```

でGitのインデックスにすべてのファイルを追加します。

```
$ git commit -m "コメント"
```

でコミットします。「コメント」部分を編集して、変更の概要を自由に記述してください。

```
$ git push origin main
```

でリモートリポジトリ(GitHub)にソースコードをアップロードします。
これで作業完了です。
