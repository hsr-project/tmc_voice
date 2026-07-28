Overview
++++++++

提供機能
--------

- 発話要求を受け付け、指定された言語で発話を作成／再生する

ROS Interface
++++++++++++++

Nodes
-----

- **text_to_speech** 言語発話ノード

Action Interfaces
^^^^^^^^^^^^^^^^^

- **talk_request_action** (:ros:action:`tmc_voice_msgs/action/TalkRequest`) 発話アクション
    ロボットが発話中の場合、その発話をキャンセルして発話する。


Subscribed Topics
^^^^^^^^^^^^^^^^^

- **talk_request** (:ros:msg:`tmc_voice_msgs/msg/Voice`) 音声用テキスト
    ロボットが発話中の場合、その発話をキャンセルして発話する。
    発話キューに積む機能は廃止された。


Published Topics
^^^^^^^^^^^^^^^^

- **talking_sentence** (:ros:msg:`std_msgs/msg/String`) 発話中のテキスト
    発話開始時にそのテキストを、発話完了時に空の文字列を発行する。


Parameter
^^^^^^^^^

- **~root_path** (string: '/opt/tmc') 音声ライセンスのルートパス

- **~pitch** (int: -1) 音声の高低を指定[%]
    初期値は100%に設定。
    pitchの範囲は50〜200%であり、数字が小さいほど低い音になる。
    -1 の場合、初期値を使用する。

- **~speed** (int: -1) 音声の速度[%]
    初期値は100%に設定。
    speedの範囲は50〜400%であり、数字が小さいほど速度が遅い音になる。
    -1 の場合、初期値を使用する。

- **~volume** (int: -1) 音声の音量[%]
    初期値は100%に設定。
    volumeの範囲は0〜500%であり、数字が小さいほど小さい音になる。
    -1 の場合、初期値を使用する。

- **~pause** (int: -1) 音声の文章間ポーズ[msec]
    初期値は800msecに設定。
    pauseの範囲は0〜65535msecであり、数字が小さいほどポーズが短くなる。
    -1 の場合、初期値を使用する。

- **~jpn_voice** (string[]: ['haruka']) 日本語の音声ライセンス名

- **~eng_voice** (string[]: ['julie']) 英語の音声ライセンス名

How to use
++++++++++

Pythonライブラリ
----------------

``tmc_talk_hoya_py`` はPythonのライブラリとしても利用可能である。
ただし実行するには、VoiceTextのライセンスがインストールされている事が必要である。

Pythonから発話させるサンプル

.. code-block:: python

   import tmc_talk_hoya_py
   speaker = tmc_talk_hoya_py.VoiceTextSpeaker(voice='haruka')
   speaker.speak(u"こんにちは")

Pythonから音声ファイルを生成させるサンプル

.. code-block:: python

   import tmc_talk_hoya_py
   voicetext = tmc_talk_hoya_py.VoiceText(voice='haruka')
   voicetext.to_file(u"こんにちは", "/tmp/sample.wave")

上記で生成されたファイルは以下のようにすれば再生可能である。

.. code-block:: bash

   $ aplay -f S16_LE -t raw -r 16000 /tmp/sample.wave

Internal
++++++++

.. ifconfig:: internal

   振る舞い:
   * 発話要求を受け取った場合、指定された言語、音声ライセンスに基づいて発話を作成／再生する
