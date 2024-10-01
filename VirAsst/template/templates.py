


class Template:
    def __init__(self):
        pass

    def get_prompt_from_task(self, task: str = None, message: str = None):
        if task == "chat":
            prompt = message + " \n" + "Generate a short and simple response."
        elif task.lower() == "summarize":
            prompt = f"Summarize the following text: {message}"
        elif task.lower() == "rephrase":
            prompt = f"Rephrase the following text {message}"
        elif task.lower() == "fix grammar":
            prompt = f"Fix the grammar in the following text:\n {message}"
        elif task.lower() == "brainstorm":
            prompt = f"Brainstorm ideas related to: {message}"
        elif task.lower() == "write email":
            prompt = f"Write an email about: {message}"
        elif task.lower() == "chat":
            prompt = f"Chat with the user about: {message}"
        else:
            prompt = message
        return prompt


    def get_template(self, user_input: str, previous_conversation: list, task: str):
        context = "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in previous_conversation])

        query = self.get_prompt_from_task(task, user_input)
        return f"Context: {context}\n\nDo the following task: {query}"