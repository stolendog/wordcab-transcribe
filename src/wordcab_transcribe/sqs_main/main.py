from wordcab_transcribe.services.queue.handler import MessageHandler
from wordcab_transcribe.queue.consumer.sqs import SQSConsumer
from wordcab_transcribe.services.queue.transcribe_handler import TranscriptionOnlyHandler

def transcription_only_cosumer(queue_name: str) -> None:
    message_transcription_handler = TranscriptionOnlyHandler()

    

    consumer = SQSConsumer(
        region_name='eu-central-1',
        queue_name=queue_name,
        message_handler=message_transcription_handler
    )

    consumer.consume_messages()

if __name__ == "__main__":
    transcription_only_cosumer("test-jonas")


# to run it 

# PYTHONPATH="/app/src:$PYTHONPATH" python -m src.wordcab_transcribe.sqs_main.main

# python -m src.wordcab_transcribe.sqs_main.main

# docker run -it --rm -v "$(pwd)/src:/app/src" -v ~/.cache:/root/.cache -e WHISPER_MODEL="tiny.en" -e COMPUTE_TYPE="int8" -e ENABLE_PUNCTUATION_BASED_ALIGNMENT="False" -e PYTHONPATH="/app/src" us-docker.pkg.dev/seldoncortex/wordcab-transcribe/main-branch:no_hatch_v3 bash