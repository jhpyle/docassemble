# do not pre-load
import openai
from docassemble.base.util import get_config, DAObject

openai.api_key = get_config('openai key')


class Conversation(DAObject):

    def init(self, *pargs, **kwargs):
        self.conversation = []
        super().init(*pargs, **kwargs)

    def ask(self, prompt):
        self.conversation.append({"role": "user", "content": prompt})
        completion = openai.chat.completions.create(
            model="gpt-5",
            messages=self.conversation
        )
        response = completion.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": response})
        return response
