# do not pre-load
import openai
from docassemble.base.util import get_config, BackgroundAction, action_argument

openai.api_key = get_config('openai key')


class Conversation(BackgroundAction):

    def init(self, *pargs, **kwargs):
        self.conversation = []
        super().init(*pargs, **kwargs)

    def call_api(self, prompt):
        self.conversation.append({"role": "user", "content": prompt})
        completion = openai.chat.completions.create(
            model="gpt-5",
            messages=self.conversation
        )
        return completion.choices[0].message.content

    def ask(self, prompt):
        response = self.run(self.attr_name('bg_ask'), prompt=prompt)
        self.conversation.append({"role": "user", "content": prompt})
        self.conversation.append({"role": "assistant", "content": response})
        return response
