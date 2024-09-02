yue Translator



Project Outline
---------------

1) Preprocess audio (reduce noice, normalize, voice detection using silero-vad)
2) Analyze audio using sensevoice 
   SenseVoice unterstützt die Erkennung von mehr als 50 Sprachen und 
   seine Erkennungsergebnisse in Chinesisch und Kantonesisch sind besser
   als das Whisper-Modell und verbessern sich um mehr als 50 %.
   + https://github.com/FunAudioLLM/SenseVoice
   + https://github.com/modelscope/FunASR 
   What about ParaformerZH (on par with SenseVoice)
3) split is using jieba?
   Hmm :/ https://medium.com/@kyubi_fox/evaluating-cantonese-performance-in-nlp-systems-8bcc3c916b71
   + use CKIP over PyCantonese 
   + I picked the best performance model bert-base.
4) Translate it using CantoneseTranslator (using best available model)
   + https://github.com/kenrickkung/CantoneseTranslation.git
5) Put it all together in a GRadio App

Prequesites
-----------

SAMPLES
+ https://voiceovers.asia/wp-content/uploads/2021/08/Leonard_Caltex_Techron_Cantonese.mp3
+ wget https://upload.wikimedia.org/wikipedia/commons/5/5b/Zh-yue-%E4%B8%81%E8%9F%B9%E6%95%88%E6%87%89%28%E4%B8%8B%29.ogg

DOCU
----
+ Auto-Download of translation models on initial run (may take a while, need
5GB of space)
+ https://github.com/ingeniela/simtracan-translator
+ https://www.cantonesetools.org/de/cantonese-stroke-order-tool
