"""The simplest demonstration how controller may work"""
from swiftbots.types import IChatView
from swiftbots.controllers import Controller


class CalculatorApi(Controller):

    async def add(self, view: IChatView, context: dict):
        """Add two numbers"""
        message = context['arguments']
        self.warn(f'User is requesting ADD operation: {message}')
        num1, num2 = message.split(' ')
        result = float(num1) + float(num2)
        await view.send_async(str(result), context)

    async def subtract(self, view: IChatView, context: dict):
        """Subtract two numbers"""
        message = context['arguments']
        self.warn(f'User is requesting SUBTRACT operation: {message}')
        num1, num2 = message.split(' ')
        result = float(num1) - float(num2)
        await view.send_async(str(result), context)

    async def kek(self, view: IChatView, context: IChatView.Context):
        context.message
        await view.send_async(f'The message is {context["message"]}', context)

    cmds = {
        'add': add,
        'sub': subtract
    }

    default = kek