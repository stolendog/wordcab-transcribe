

"""Tests the delete_file function."""
from wordcab_transcribe.services.queue.transcribe_handler import TranscriptionOnlyHandler


def test_transcription_only_handler() -> None:
    handler = TranscriptionOnlyHandler()
    analyzed_filepath = handler.analyze_audio("audio_url_7AtVQutR4FtGFmJFgQ4YfBNR8NsZNG6J_1714125106160846682.wav", multi_channel=False)

    print(type(analyzed_filepath))

    tensor_tuple = handler.convert_to_audio_tensor(analyzed_filepath, None, None)



test_transcription_only_handler()