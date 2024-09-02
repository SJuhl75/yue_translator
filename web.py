import torch
import gradio as gr
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps #, read_audio, save_audio
import noisereduce as nr
import numpy as np
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
import re
import gdown
import sys
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pycantonese
from googletrans import Translator

# Borrowed from CantoneseTranslation-Backend, due to little bug
class CanTranModel:
    def __init__(self, model_path="models/nllb-zh/nllb-forward-1t1"):
        self.device = self.get_device()
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        
    def init_model_and_tokenizer(self):
      if self.tokenizer is None or self.model is None:
        self.tokenizer = AutoTokenizer.from_pretrained(
            "facebook/nllb-200-distilled-600M",	# TODO Improvement?
            src_lang="yue_Hant",
            tgt_lang="eng_Latn",
            legacy_behaviour=True,
            clean_up_tokenization_spaces=True
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_path,
            local_files_only=True
        )
        self.model.to(self.device)
        self.model.eval()

    def get_device(self):
        if torch.cuda.is_available():
            return torch.device("cuda")
        elif torch.backends.mps.is_available():
            return torch.device("mps")
        else:
            return torch.device("cpu")

    def translate(self, text):
        self.init_model_and_tokenizer()
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        eng_lang_code = self.tokenizer.convert_tokens_to_ids("eng_Latn")
        translated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=eng_lang_code,
#            max_length=30
        )
        return self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]


# Check availability of CUDA
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Initialize Silero VAD
silvad = load_silero_vad()

model_dir = "iic/SenseVoiceSmall"
asrmodel = AutoModel(
            model=model_dir,
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            device=f"{device}:0",
            disable_update=True)

ct_model = CanTranModel()

# Initialize Google Translator
translator = Translator()

# Load pre-trained model and tokenizer
#model_name = "facebook/bart-large"
#tokenizer = BartTokenizer.from_pretrained(model_name)

# Function to download the folder and create the directory structure
def create_directory_structure(subdir, folder_id, symlink_name):
    # Create the subdirectory path
    subdir_path = os.path.join(models_dir, subdir)
    
    # Ensure the subdirectory exists
    if not os.path.exists(subdir_path):
        os.makedirs(subdir_path)
        #print(f"Created directory: {subdir_path}")
    
    # Construct the Google Drive URL
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    
    # Download the folder using gdown
    downloaded_files = gdown.download_folder(url, output=f"{subdir_path}/", quiet=False)
    
    # Get the folder path from the first file in the list
    first_file_path = downloaded_files[0]
    downloaded_folder_path = os.path.dirname(first_file_path)
    
    # Create the symbolic link
    symlink_path = os.path.join(subdir_path, symlink_name)
    downloaded_folder_path = downloaded_folder_path.removeprefix(f"{subdir_path}/")
    os.symlink(downloaded_folder_path, symlink_path)
    #print(f"Created symbolic link: {symlink_path} -> {downloaded_folder_path}")

# Check if model subdir already exists and if necessary download required files
models_dir = 'models'
if not os.path.exists(models_dir):
    os.makedirs(models_dir)
    
    # Subdir, Google Drive ID, symbolic link name of models
    data = [
        # ('mbart-zh', '1-aGK20YvpB6xJT561g-461dcYC-sA9pW', 'Synthetic-1t1-NLLB'),
          ('nllb-zh', '1lNwnv2g5C745B0O-arKEgY62Uijk8B5U', 'nllb-forward-1t1'),
        # ('opus-zh', '13wW9fGuAcRF9Vlo-ZREb7oTe3Hmk-Ctn', 'opus-mt-zh-en-finetuned'),
    ]
    for subdir, folder_id, symlink_name in data:
        create_directory_structure(subdir, folder_id, symlink_name)


# Define a function to split the audio into chunks of 512 samples
def split_audio_into_chunks(audio, sr, chunk_size_samples):
    chunk_list = []
    num_chunks = len(audio) // chunk_size_samples
    for i in range(num_chunks):
        chunk = audio[i * chunk_size_samples:(i + 1) * chunk_size_samples]
        chunk_list.append(chunk)
    return chunk_list

# Define a function to reassemble the selected chunks into a single waveform
def reassemble_chunks(selected_chunks):
    if selected_chunks:
        return np.concatenate(selected_chunks)
    else:
        return np.array([])  # Return an empty array if no chunks are selected

def preprocess_audio(v_wav,v_sr):  
    # Set padding seconds, calculate number of zero samples
    pad_duration = 1.0  # Example: 1 second of padding
    pad_samples = int(pad_duration * v_sr)

    # Load and preprocess audio
    paudio = nr.reduce_noise(y=v_wav,sr=v_sr)			# Noise Reduction
    paudio = (paudio - np.mean(paudio)) / np.std(paudio)  	# Normalization
    paudio = torch.from_numpy(paudio)				# Convert back to a tensor

    # Create the padding chunk filled with zeros
    padding = torch.zeros(pad_samples, dtype=paudio.dtype) 

    # Split audio into chunks of 512 samples
    chunk_size_samples = 512  # for 16000 Hz sample rate
    chunk_list = split_audio_into_chunks(paudio, v_sr, chunk_size_samples)

    # Set the speech probability threshold
    threshold = 0.5

    # Create attention mask based on VAD
    attention_mask = []

    # Store selected chunks that are above the threshold
    selected_chunks = []

    # Process each chunk using the VAD model
    for chunk in chunk_list:
        speech_prob = silvad(chunk, v_sr).item()
        if speech_prob > threshold:
            #padded_chunk = torch.cat((padding, chunk, padding))
            selected_chunks.append(chunk)    # Add chunk to selected_chunks if it meets the threshold
#            selected_chunks.append(padding)  # Add chunk to selected_chunks if it meets the threshold
#            print(f"chunk {chunk.type} {chunk.dtype}")
#            print(f"padding {padding.type} {padding.dtype}")

    # Reset model states after processing the audio
    silvad.reset_states()

    # Reassemble selected chunks into a single waveform
    final_wav = reassemble_chunks(selected_chunks)
    return final_wav	#, attention_mask

def translate_text(text, target_language):
    segments = text.split(',')  # Split the text at commas
    translated_segments = []

    for segment in segments:
        translated_segment = translator.translate(segment.strip(), dest=target_language).text
        translated_segments.append(translated_segment)

    return ', '.join(translated_segments)  # Rejoin the segments with commas
   
def split_with_multiple_delimiters(text):
    # Define delimiters
    delimiters = ["。", "！", "？"]

    # Create a regex pattern that matches any of the delimiters
    pattern = '|'.join(map(re.escape, delimiters))
    
    # Split the text while keeping the delimiters as part of the results
    parts = re.split(f'({pattern})', text)
    
    # Join each part with its corresponding delimiter
    return [parts[i] + parts[i + 1] for i in range(0, len(parts) - 1, 2)]

def apply_vad_and_transcribe(audio_file):
    try:
        # Load audio   wav, sr = librosa.load(audio_file, sr=16000)
        sr = 16000
        wav = read_audio(audio_file, sampling_rate=sr)
        print(f"Loaded audio with sample rate {sr}")

        # Pre-Process audio file
        print("Pre-Processing audio file...")
        #audio, att_mask = preprocess_audio(wav,sr)  
        audio = preprocess_audio(wav,sr)

        res = asrmodel.generate(
            #    input=f"{model.model_path}/example/yue.mp3",
            input=audio, #"../Zh-yue-同位異音.ogg.mp3",
            cache={},
            language="auto",  # "zn", "en", "yue", "ja", "ko", "nospeech"
            use_itn=True,
            batch_size_s=60,
            merge_vad=True,  #
            merge_length_s=15,
            )
        transcription = rich_transcription_postprocess(res[0]["text"])
        print("Transcription:",res)

        # Remove tags like <|yue|>, <|HAPPY|>, etc.
        clean_transcript = re.sub(r'<\|.*?\|>', '', transcription)

        # Split the text using the multiple delimiters
        #parts=split_with_multiple_delimiters(clean_transcript)

        # Pass each part to the user-defined function
        #translation_en = ""
        #for part in parts:
        #    translation = ct_mdel.translate(part)
        #    print(f"Translation: {translation}")
        #    translation_en.join(translation)
        translation_en = ct_model.translate(clean_transcript)
        print(f"Translation: {translation_en}")

        # PyCantonese
        words = pycantonese.segment(transcription) #"廣東話好難學？")  # Is Cantonese difficult to learn?
        transcription = ' '.join(words)
        print("transcription=",transcription)

        print("Translating to German...",clean_transcript)
        translation_de = translator.translate(clean_transcript, src='auto', dest='de').text
        print(f"Translation (DE): {translation_de}")

        return transcription, translation_en, translation_de

    except Exception as e:
        # Capture the error message and return it
        error_message = f"Error: {str(e)}"
        print(error_message)
        return error_message, "", ""

# MAIN Create Gradio interface

iface = gr.Interface(
    fn=apply_vad_and_transcribe,
    inputs=[
        gr.Audio(type="filepath", label="Upload Audio (.ogg, .mp3, .wav)")
    ],
    outputs=[
        gr.Textbox(label="Transcription (PyCantonese)", show_copy_button=True),
        gr.Textbox(label="English translation (NLLB-forward-1:1)", show_copy_button=True),
        gr.Textbox(label="German translation (Google-Translate)", show_copy_button=True)
    ],
    allow_flagging="never",
#    live=True
)

# Launch Gradio app
iface.launch(server_name="0.0.0.0", server_port=7867)
