from typing import List
from agentos.models.message import Message


class MessagingHub:
    def __init__(self) -> None:
        self._messages: List[Message] = []

    def send(self, message: Message) -> None:
        self._messages.append(message)
        print(
            f"[Message][SEND] "
            f"{message.from_role} -> {message.to_role} "
            f"type={message.message_type} "
            f"task_id={message.task_id} "
            f"msg_id={message.message_id}"
        )

    def fetch_for_role(self, role_id: str, project_id: str) -> List[Message]:
        msgs = [
            m for m in self._messages
            if m.to_role == role_id
            and m.project_id == project_id
            and m.status == "sent"
        ]
        if msgs:
            print(
                f"[Message][FETCH] role={role_id} "
                f"project_id={project_id} "
                f"count={len(msgs)}"
            )
        return msgs

    def mark_processed(self, message_id: str) -> None:
        for msg in self._messages:
            if msg.message_id == message_id:
                msg.status = "processed"
                print(
                    f"[Message][PROCESSED] "
                    f"{msg.from_role} -> {msg.to_role} "
                    f"type={msg.message_type} "
                    f"task_id={msg.task_id} "
                    f"msg_id={msg.message_id}"
                )
                return

    def list_all(self) -> List[Message]:
        return list(self._messages)
