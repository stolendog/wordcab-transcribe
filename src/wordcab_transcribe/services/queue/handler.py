from pydantic import BaseModel

class MessageHandler:
    def deserialize(self, message_body: str) -> BaseModel:
        """Deserialize the message body to a Pydantic model."""
        raise NotImplementedError("Handlers must implement deserialization.")

    def process(self, message: BaseModel):
        """Process a Pydantic model instance."""
        raise NotImplementedError("Handlers must implement this method.")
