**yue Translator**
-----------------
Cantonese transcription and translation using the best open source tools available, running locally in a fair-well GPU-powered environment.
Automatic download of translation models on first run may take a while, and roughly requires 5GB of additional disk space.
Web interface is available via port 7867

Basic Workflow of the Web App
-----------------------------
1)   Upload of Audio files
2)   Preprocess audio (reduce noice, normalize, voice activity detection using silero-vad -> https://github.com/snakers4/silero-vad).
3)   Transcribe audio using the FunASR framework with the SenseVoice model, which outperforms whisper (see https://arxiv.org/html/2407.04051v2).
      + https://github.com/FunAudioLLM/SenseVoice
      + https://github.com/modelscope/FunASR 
4)   Use PyCantonese to segement cantonese words (-> https://pycantonese.org/)
5)   Use of Canto-filter to categorize language of the words transcribed (-> https://github.com/CanCLID/canto-filter)
6)   If an OPENAI_API_KEY is provided, use GPT-3.5-turbo-16k for translation. Otherwise translate the transcribed text using CantoneseTranslator, using the best available model (= NLLB, see https://github.com/kenrickkung/CantoneseTranslation.git). The quality of the translation is comparable to Baidu or Bing Translator.

Notes on Translation
--------------------
The SacreBLEU score of the nllb-forward-syn-1:1-mbart model used for local
on premises translation is 16.8. This is on a par with the Baidu translator
(16.6), but below the top scores of Bing Translator (17.1) or ChatGPT's Cantonese
Companion (19.2) - that's why usage of an OpenAI API key is highly recommended.
+	https://chatgpt.com/g/g-749lHuJQB-cantonese-companion
+	https://www.bing.com/translator
+	https://fanyi.baidu.com/

Installation
------------
1)   python -m venv venv
2)   source venv/bin/activate
3)   pip install -r requirements.txt
4)   python web.py

Future Work?
------------
-   What about ParaformerZH (on par with SenseVoice)
-   Tokenizer? https://medium.com/@kyubi_fox/evaluating-cantonese-performance-in-nlp-systems-8bcc3c916b71
-   Use CKIP instead of PyCantonese?
   
*Other useful ressources:*
+ https://github.com/ingeniela/simtracan-translator
+ https://www.cantonesetools.org/de/cantonese-stroke-order-tool
