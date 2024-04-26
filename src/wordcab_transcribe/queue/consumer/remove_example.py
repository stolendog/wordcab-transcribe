import asyncio
import json
from datetime import datetime
from typing import TYPE_CHECKING, Awaitable, Dict, List, Optional, Tuple, Union

import torch
import torchaudio
import shortuuid

from tensorshare import Backend, TensorShare

from wordcab_transcribe.services.asr_service import ASRTranscriptionOnly, ASRService

from wordcab_transcribe.models import (
    TranscribeRequest,
    TranscriptionOutput,
)

from wordcab_transcribe.services.asr_service import TranscriptionOptions, ProcessException

from wordcab_transcribe.utils import (
    check_num_channels,
    delete_file,
    download_audio_file,
    process_audio_file,
    read_audio,
)

# from wordcab_transcribe.consumer.whisper import print_speech



url = "https://www2.cs.uic.edu/~i101/SoundFiles/preamble10.wav"


# request_data = TranscribeRequest(
    
# )

def convert_audio_tensor(
        filepath: Union[str, List[str]], 
        offset_start: Union[float, None], 
        offset_end: Union[float, None]
) -> Tuple[torch.Tensor, float]:
    if isinstance(filepath, list):
        audio, durations = [], []
        for path in filepath:
            _audio, _duration = read_audio(
                path, offset_start=offset_start, offset_end=offset_end
            )

            audio.append(_audio)
            durations.append(_duration)

        duration = sum(durations) / len(durations)
    else:
        audio, duration = read_audio(
            filepath, offset_start=offset_start, offset_end=offset_end
        )

    return [audio, duration]

def convert_to_tensorshare(audio_data):
    if isinstance(audio_data, list):
        ts = [
            TensorShare.from_dict({"audio": a}, backend=Backend.TORCH)
            for a in audio_data
        ]
    else:
        ts = TensorShare.from_dict(
            {"audio": audio_data}, backend=Backend.TORCH
        )
    return ts

async def transcribe_from_url(multi_channel: bool = False) -> None:
    filename = f"audio_url_{shortuuid.ShortUUID().random(length=32)}"
    _filepath = await download_audio_file("url", url, filename)

    # num_channels = await check_num_channels(_filepath)
    # if num_channels > 1 and multi_channel is False:
    #     num_channels = 1  # Force mono channel if more than 1 channel

    # try:
    #     filepath: Union[str, List[str]] = await process_audio_file(
    #         _filepath, num_channels=num_channels
    #     )

    # except Exception as e:
    #     raise Exception( 
    #         detail=f"Process failed: {e}",
    #     )

    # delete_file(filename)

    # audio , duration = convert_audio_tensor(filepath, offset_start=None, offset_end=None)
    # ts_audio = convert_to_tensorshare(audio)

    # asr_trascription_only_service = ASRTranscriptionOnly(
    #     # whisper_model="tiny.en",
    #     whisper_model="medium.en",
    #     model_engine="faster-whisper",
    #     compute_type="default",
    #     extra_languages=None,
    #     extra_languages_model_paths=None,
    #     debug_mode=True,
    # )

    # # await asr_trascription_only_service.inference_warmup()


    # # transcription_options = TranscriptionOptions(
    # #     compression_ratio_threshold=compression_ratio_threshold,
    # #     condition_on_previous_text=condition_on_previous_text,
    # #     internal_vad=internal_vad,
    # #     log_prob_threshold=log_prob_threshold,
    # #     no_speech_threshold=no_speech_threshold,
    # #     repetition_penalty=repetition_penalty,
    # #     source_lang=source_lang,
    # #     vocab=vocab,
    # # )

    # data = TranscribeRequest(
    #     audio=ts_audio,
    #     compression_ratio_threshold=2.4,
    #     condition_on_previous_text=True,
    #     internal_vad=False,
    #     log_prob_threshold=-1.0,
    #     repetition_penalty=1.2,
    #     no_speech_threshold=0.6,
    #     source_lang="en",
    #     vocab=None,
    #     batch_size=1,
    # )

    # transcription_output = await asr_trascription_only_service.process_input(data=data)

    # if isinstance(transcription_output, ProcessException):
    #     raise Exception( 
    #         detail=f"Process failed: {transcription_output}",
    #     )
    # else:
    #     print_speech(transcription_output.segments)



asyncio.run(transcribe_from_url())
# asr_service = ASRService()

