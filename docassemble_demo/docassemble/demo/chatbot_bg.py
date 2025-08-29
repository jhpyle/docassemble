# do not pre-load
import openai
from docassemble.base.util import get_config, DAObject, background_action

openai.api_key = get_config('openai key')


class Conversation(DAObject):

    def init(self, *pargs, **kwargs):
        self.conversation = []
        self.stage = 0
        super().init(*pargs, **kwargs)

    def fg_ask(self, prompt):
        self.conversation.append({"role": "user", "content": prompt})
        completion = openai.chat.completions.create(
            model="gpt-5",
            messages=self.conversation
        )
        response = completion.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": response})
        return response

    def ask(self, prompt):
        if self.stage == 0:
            self.bg_action = background_action(self.attr_name('bg_ask'), prompt=prompt)
            self.stage = 1
            self.wait
        if self.stage == 1:
            if not self.bg_action.ready():
                self.wait
            response = self.bg_action.get()
            self.conversation.append({"role": "user", "content": prompt})
            self.conversation.append({"role": "assistant", "content": response})
            self.stage = 0
            del self.bg_action
            return response
        return "error"
