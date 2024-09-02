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
5)   Translate the transcribed text using CantoneseTranslator, using the best available model (= NLLB, see https://github.com/kenrickkung/CantoneseTranslation.git).
The quality of the translation is comparable to Baidu or Bing Translator.

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
-   Classify trascribed text using https://github.com/CanCLID/canto-filter#cantonese-text-classifier?
   
*Other useful ressources:*
+ https://github.com/ingeniela/simtracan-translator
+ https://www.cantonesetools.org/de/cantonese-stroke-order-tool
