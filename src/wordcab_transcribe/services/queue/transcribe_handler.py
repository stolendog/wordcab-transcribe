import json
import asyncio
from typing import List, Optional, Union, Tuple

from pydantic import BaseModel

import shortuuid
import torch

from tensorshare import Backend, TensorShare

from wordcab_transcribe.services.asr_service import ASRTranscriptionOnly, ProcessException
from wordcab_transcribe.services.queue.handler import MessageHandler

from wordcab_transcribe.models import InferenceUrlRequest, TranscribeRequest
from wordcab_transcribe.config import settings

from wordcab_transcribe.utils import (
    check_num_channels,
    delete_file,
    download_audio_file,
    process_audio_file,
    read_audio,
)



class TranscriptionOnlyHandler(MessageHandler):
    def __init__(self) -> None:
        super().__init__()
        self.transcription_service = ASRTranscriptionOnly(
            model_engine="faster-whisper",
            whisper_model=settings.whisper_model,
            compute_type=settings.compute_type,
            extra_languages=settings.extra_languages,
            extra_languages_model_paths=settings.extra_languages_model_paths,
            debug_mode=settings.debug,
        )
        asyncio.run(self.transcription_service.inference_warmup())

        # await self.transcription_service.inference_warmup()

    def download_audio_file(self, url: str) -> str:
        filepath = f"audio_url_{shortuuid.ShortUUID().random(length=32)}"
        asyncio.run(download_audio_file("url", url, filepath))
        return filepath
    
    def analyze_audio(self, filepath: str, multi_channel: bool) -> Union[str, List[str]]:
        num_channels = asyncio.run(check_num_channels(filepath))
        if num_channels > 1 and not multi_channel:
            num_channels = 1  # Force mono channel if more than 1 channel
        
        try:
            analyzed_filepath: Union[str, List[str]] = asyncio.run(process_audio_file(
                filepath, num_channels=num_channels
            ))

        except Exception as e:
            raise ProcessException(f"Audio file analysis failed: {e}") from e
        
        return analyzed_filepath
    
    def convert_to_audio_tensor(
        self,
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
    
    def convert_to_tensorshare(self, audio_data):
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

    def deserialize(self, message_body: str) -> InferenceUrlRequest:
        return InferenceUrlRequest(**json.loads(message_body))
    
    def process(self, request: InferenceUrlRequest):
        print(f"Processing request: {request}")
        filepath = self.download_audio_file(request.url)
        analyzed_filepath = self.analyze_audio(filepath, request.data.multi_channel)

        print(analyzed_filepath)

        audio , duration = self.convert_to_audio_tensor(
            filepath = analyzed_filepath, 
            offset_start = request.data.offset_start, 
            offset_end = request.data.offset_end
        )
        ts_audio = self.convert_to_tensorshare(audio)
        
        transcribeRequest = TranscribeRequest(
            audio=ts_audio,
            **request.data.model_dump()
        )

        transcription_output = asyncio.run(self.transcription_service.process_input(transcribeRequest))

        if isinstance(transcription_output, ProcessException):
            raise Exception(f"Process failed: {transcription_output}")
        else:
            print_speech(transcription_output.segments)


from datetime import timedelta

def print_speech(segments: list) -> None:
    for segment in segments:
        startTime = str(0)+str(timedelta(seconds=int(segment.start)))+',000'
        endTime = str(0)+str(timedelta(seconds=int(segment.end)))+',000'
        text = segment.text
        s_text = f"{segment.id}\n{startTime} --> {endTime}\n{text[1:] if text[0] == ' ' else text}\n\n"
        print(s_text)