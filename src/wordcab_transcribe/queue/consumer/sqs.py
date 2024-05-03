import boto3
import time
import threading

from botocore.config import Config

from wordcab_transcribe.services.queue.handler import MessageHandler

class SQSConsumer:
    """SQS Consumer class."""

    def __init__(self, region_name, queue_name, message_handler: MessageHandler):
        self.queue = boto3.resource('sqs', config=Config(
            region_name=region_name,
        )).get_queue_by_name(QueueName=queue_name)
        self._message_handler = message_handler

    def _extend_visibility(self, message, interval, keep_running):
        """
        Extend the visibility timeout of the message while it's being processed.
        """
        # TODO: max extention limit 1h
        while keep_running():
            new_timeout = interval + 10  # Extend timeout beyond the sleep period
            message.change_visibility(VisibilityTimeout=new_timeout)
            print(f"Visibility timeout extended by {new_timeout} seconds. For message {message.body}.")
            time.sleep(interval)

    def consume_messages(self):
        while True:
            print("waiting for messages")
            messages = self.queue.receive_messages(
                # AttributeNames=['CreatedTimestamp','MessageDeduplicationId','DelaySeconds', 'SenderId'],
                MaxNumberOfMessages=1,
                WaitTimeSeconds=5
            )

            for message in messages:
                keep_running = True

                def keep_running():
                    return keep_running

                print(f"Got a message: \"{message.body}\" attr: {message.attributes}")
                extender_thread = threading.Thread(target=self._extend_visibility, args=(message, 20, keep_running))
                extender_thread.start()

                try:
                    msg = self._message_handler.deserialize(message.body)
                    self._message_handler.process(msg)
            
                    print(f"waiting for extender to finish")
                    keep_running = False
                    message.delete()
                    print(f"message deleted")
                    extender_thread.join()
                except Exception as e:
                    print(f"Failed to process message: {e}")
                    message.delete()
                    keep_running = False
