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