from docassemble.base.util import get_config, DAObject, BackgroundAction, DADict
import anthropic

__all__ = ['AIHelper', 'AIInteraction']

client = anthropic.Anthropic(api_key=get_config('anthropic api key'))

tools = [
    {
        "name": "conversation_complete",
        "description": "Call this tool when you have collected all necessary information from the user.",
        "input_schema": {
            "type": "object",
            "properties": {
                "output": {
                    "type": "string",
                    "description": "The output that was requested of you"
                }
            },
            "required": ["output"]
        }
    }
]


class Conversation(DAObject):
    def init(self, *pargs, **kwargs):
        self.conversation = []
        self.done = False
        super().init(*pargs, **kwargs)

    def ask(self, system_prompt, prompt):
        str(system_prompt)
        self.conversation.append({"role": "user", "content": prompt})
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024*8,
            system=str(system_prompt),
            tools=tools,
            messages=self.conversation
        )
        tool_use_block = None
        text_blocks = []
        for block in response.content:
            if block.type == "tool_use" and block.name == "conversation_complete":
                tool_use_block = block
            elif block.type == "text":
                text_blocks.append(block.text)
        if tool_use_block:
            result = tool_use_block.input
            self.done = True
            self.output = result['output']
            return self.output
        self.conversation.append({"role": "assistant", "content": response.content})
        return ' '.join(text_blocks)


class AIInteraction(DAObject):
    def init(self, *pargs, **kwargs):
        self.initializeAttribute('conv', Conversation)
        self.started = False
        super().init(*pargs, **kwargs)

    def interact(self):  # pylint: disable=inconsistent-return-statements
        if not self.started:
            str(self.prompt)
            self.output = str(self.initial_output)
            self.input  # pylint: disable=pointless-statement
            self.started = True
        if self.conv.done:
            self.delattr('bg')
            return self.output
        if not hasattr(self, 'bg'):
            sys_prompt = str(self.prompt)
            prompt = self.input
            self.initializeAttribute('bg', BackgroundAction)
            self.bg.run(self.attr_name('prompt_ai'), system_prompt=sys_prompt, user_input=prompt)
        self.bg.run(self.attr_name('prompt_ai'))
        self.delattr('input')
        self.delattr('bg')
        self.input  # pylint: disable=pointless-statement


class AIHelper(DADict):
    def init(self, *pargs, **kwargs):
        self.object_type = AIInteraction
        super().init(*pargs, **kwargs)
