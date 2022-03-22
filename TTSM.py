import tensorflow as tf

import yaml
import os
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import re


from tensorflow_tts.inference import AutoConfig
from tensorflow_tts.inference import TFAutoModel
from tensorflow_tts.inference import AutoProcessor

# Load Chinese Models
tacotron2 = TFAutoModel.from_pretrained("tensorspeech/tts-tacotron2-baker-ch", name="tacotron2")

mb_melgan = TFAutoModel.from_pretrained("tensorspeech/tts-mb_melgan-baker-ch", name="mb_melgan")

processor = AutoProcessor.from_pretrained("tensorspeech/tts-tacotron2-baker-ch")

fastspeech2 = TFAutoModel.from_pretrained("tensorspeech/tts-fastspeech2-baker-ch", name="fastspeech2")

# Load English Models

tacotron2_en = TFAutoModel.from_pretrained("tensorspeech/tts-tacotron2-ljspeech-en", name="tacotron2")

mb_melgan_en = TFAutoModel.from_pretrained("tensorspeech/tts-mb_melgan-ljspeech-en", name="mb_melgan")

processor_en = AutoProcessor.from_pretrained("tensorspeech/tts-tacotron2-ljspeech-en")

# Compile Re rules
reEX = re.compile(r'([a-zA-Z]+)')
rex = re.compile(",|\\.|\\?|!|:|;|~|，|：|。|！|；|？|  ")

def do_synthesis(input_text, text2mel_model, vocoder_model, text2mel_name, vocoder_name):
    try:
        input_ids = processor.text_to_sequence(input_text, inference=True)
    except:
        return [0,0,0,0]

    # text2mel part
    if text2mel_name == "TACOTRON":
        _, mel_outputs, stop_token_prediction, alignment_history = text2mel_model.inference(
            tf.expand_dims(tf.convert_to_tensor(input_ids, dtype=tf.int32), 0),
            tf.convert_to_tensor([len(input_ids)], tf.int32),
            tf.convert_to_tensor([0], dtype=tf.int32)
        )
    elif text2mel_name == "FASTSPEECH2":
        mel_before, mel_outputs, duration_outputs, _, _ = text2mel_model.inference(
            tf.expand_dims(tf.convert_to_tensor(input_ids, dtype=tf.int32), 0),
            speaker_ids=tf.convert_to_tensor([0], dtype=tf.int32),
            speed_ratios=tf.convert_to_tensor([1.0], dtype=tf.float32),
            f0_ratios=tf.convert_to_tensor([1.0], dtype=tf.float32),
            energy_ratios=tf.convert_to_tensor([1.0], dtype=tf.float32),
        )
    else:
        raise ValueError("Only TACOTRON, FASTSPEECH2 are supported on text2mel_name")

    # vocoder part
    if vocoder_name == "MB-MELGAN":
        # tacotron-2 generate noise in the end symtematic, let remove it :v.
        if text2mel_name == "TACOTRON":
            remove_end = 1024
        else:
            remove_end = 1
        audio = vocoder_model.inference(mel_outputs)[0, :-remove_end, 0]
    else:
        raise ValueError("Only MB_MELGAN are supported on vocoder_name")

    if text2mel_name == "TACOTRON":
        return audio.numpy()
    else:
        return audio.numpy()


def do_synthesis_en(input_text, text2mel_model, vocoder_model, text2mel_name, vocoder_name):
    try:
        input_ids = processor_en.text_to_sequence(input_text)
    except:
        return [0,0,0,0]
    # text2mel part
    if text2mel_name == "TACOTRON":
        _, mel_outputs, stop_token_prediction, alignment_history = text2mel_model.inference(
            tf.expand_dims(tf.convert_to_tensor(input_ids, dtype=tf.int32), 0),
            tf.convert_to_tensor([len(input_ids)], tf.int32),
            tf.convert_to_tensor([0], dtype=tf.int32)
        )
    elif text2mel_name == "FASTSPEECH":
        mel_before, mel_outputs, duration_outputs = text2mel_model.inference(
            input_ids=tf.expand_dims(tf.convert_to_tensor(input_ids, dtype=tf.int32), 0),
            speaker_ids=tf.convert_to_tensor([0], dtype=tf.int32),
            speed_ratios=tf.convert_to_tensor([1.0], dtype=tf.float32),
        )
    elif text2mel_name == "FASTSPEECH2":
        mel_before, mel_outputs, duration_outputs, _, _ = text2mel_model.inference(
            tf.expand_dims(tf.convert_to_tensor(input_ids, dtype=tf.int32), 0),
            speaker_ids=tf.convert_to_tensor([0], dtype=tf.int32),
            speed_ratios=tf.convert_to_tensor([1.0], dtype=tf.float32),
            f0_ratios=tf.convert_to_tensor([1.0], dtype=tf.float32),
            energy_ratios=tf.convert_to_tensor([1.0], dtype=tf.float32),
        )
    else:
        raise ValueError("Only TACOTRON, FASTSPEECH, FASTSPEECH2 are supported on text2mel_name")

    # vocoder part
    if vocoder_name == "MELGAN" or vocoder_name == "MELGAN-STFT":
        audio = vocoder_model(mel_outputs)[0, :, 0]
    elif vocoder_name == "MB-MELGAN":
        audio = vocoder_model(mel_outputs)[0, :, 0]
    else:
        raise ValueError("Only MELGAN, MELGAN-STFT and MB_MELGAN are supported on vocoder_name")

    if text2mel_name == "TACOTRON":
        return audio.numpy()
    else:
        return audio.numpy()

def runModels(input_text):
    audio = []
    for i in reEX.split(input_text):
        i = i.replace("嗯",",是的,")
        for j in rex.split(i):
            j = strip(j)
            print(j)
            if reEX.match(j) is None:
                # tacotron2模型无法识别单字
                if len(j) > 1:
                    audios = do_synthesis(j, tacotron2, mb_melgan, "TACOTRON", "MB-MELGAN")
                elif len(j) == 1:
                    audios = do_synthesis(j, fastspeech2, mb_melgan, "FASTSPEECH2", "MB-MELGAN")
                else:
                    continue
            else:
                audios = do_synthesis_en(' ' + j + ' ', tacotron2_en, mb_melgan_en, "TACOTRON",
                                                                  "MB-MELGAN")
            audio.extend(audios)
            audio.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] * 180)
    return audio
def strip(path):
    """
    :param path: 需要清洗的文件夹名字
    :return: 清洗掉Windows系统非法文件夹名字的字符串
    """
    path = re.sub(r'[？?\*|“"<>:/]', '', str(path))
    return path
def run(text_list):
    a = []
    for text in text_list:
        a.extend(runModels(text))
    if not os.path.exists('./output/'):
        os.mkdir('./output')
    sf.write('./output/{}.wav'.format(text_list[0]), a, 24000, "PCM_16")