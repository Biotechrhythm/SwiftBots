import asyncio

from traceback import format_exc

from swiftbots.bots import Bot, close_bot_async
from swiftbots.types import StartBotException, ExitApplicationException, ExitBotException, IContext, IChatView
from swiftbots.utils import ErrorRateMonitor


__ALL_TASKS: set[str] = set()


def get_all_tasks() -> set[str]:
    return __ALL_TASKS


async def delegate_to_handler_async(bot: Bot, context: IContext) -> None:
    try:
        await bot.message_handler.handle_message_async(bot.view, context)
    except (asyncio.CancelledError, StartBotException, ExitApplicationException, ExitBotException):
        # rethrow it to runner
        raise
    except (AttributeError, TypeError, KeyError, AssertionError) as e:
        await bot.logger.critical_async(f"Fix the code! Critical python {e.__class__.__name__} "
                                        f"raised: {e}. Full traceback:\n{format_exc()}")
        if isinstance(bot.view, IChatView):
            await bot.view.error_async(context)
    except Exception as e:
        await bot.logger.error_async(f"Bot {bot.name} was raised with unhandled {e.__class__.__name__}:"
                                     f" {e} and kept on working. Full traceback:\n{format_exc()}")
        if isinstance(bot.view, IChatView):
            await bot.view.error_async(context)


async def start_async_listener(bot: Bot):
    """
    Launches all bot views, and sends all updates to their message handlers.
    Runs asynchronously.
    """
    err_monitor = ErrorRateMonitor(cooldown=60)
    generator = bot.view.listen_async()
    while True:
        try:
            pre_context = await generator.__anext__()
        except (asyncio.CancelledError, StartBotException, ExitApplicationException, ExitBotException):
            # it should be processed in the runner
            raise
        except Exception as e:
            await bot.logger.error_async(f"Bot {bot.name} was raised with unhandled {e.__class__.__name__}:"
                                         f" {e} and kept on listening. Full traceback:\n{format_exc()}")
            if err_monitor.since_start < 3:
                await bot.logger.critical_async(f"Bot {bot.name} raises immediately after start listening. "
                                                f"Shutdown this")
                raise ExitBotException()
            rate = err_monitor.evoke()
            if rate > 5:
                await bot.logger.error_async(f"Bot {bot.name} sleeps for 30 seconds.")
                await asyncio.sleep(30)
                err_monitor.error_count = 3
            generator = bot.view.listen_async()
            continue

        await delegate_to_handler_async(bot, pre_context)


async def run_async(bots: list[Bot]):
    tasks: set[asyncio.Task] = set()

    bot_names: dict[str, Bot] = {bot.name: bot for bot in bots}
    global __ALL_TASKS
    __ALL_TASKS = bot_names.keys()

    for name, bot in bot_names.items():
        task = asyncio.create_task(start_async_listener(bot), name=name)
        tasks.add(task)

    while 1:
        if len(tasks) == 0:
            return
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            name = task.get_name()
            bot = bot_names[name]
            try:
                result = task.result()
                await bot.logger.critical_async(f"Bot {name} was finished with result {result} and restarted")
            except (asyncio.CancelledError, ExitBotException) as ex:
                if ex is asyncio.CancelledError:
                    await bot.logger.warn_async(f"Bot {name} was cancelled. Not started again")
                tasks.remove(task)
                await close_bot_async(bot)
                continue
            except StartBotException as ex:
                # Special exception instance for starting bots from admin panel
                try:
                    bot_name_to_start = str(ex)
                    bot_to_start = bot_names[str(ex)]
                    new_task = asyncio.create_task(start_async_listener(bot_to_start), name=bot_name_to_start)
                    tasks.add(new_task)
                except Exception as e:
                    await bot.logger.critical_async(f"Couldn't start bot {ex}. Exception: {e}")
                continue
            except ExitApplicationException:
                for bot_to_exit in bot_names.values():
                    await close_bot_async(bot_to_exit)
                await bot.logger.report_async("Bots application was closed")
                return

            tasks.remove(task)
            new_task = asyncio.create_task(start_async_listener(bot), name=name)
            tasks.add(new_task)
