__all__ = [
    'task',
    'TaskInfo'
]

from typing import List, Union

from swiftbots.all_types import ITrigger


class TaskInfo:
    def __init__(self,
                 name: str,
                 triggers: List[ITrigger],
                 run_at_start: bool):
        self.name = name
        self.triggers = triggers
        self.run_at_start = run_at_start


def task(
    name: str,
    triggers: Union[ITrigger, List[ITrigger]],
    run_at_start: bool = False
):
    """
    Mark a controller method as a task.
    Depends on trigger(s), will be executed by scheduler.
    """
    assert isinstance(triggers, ITrigger) or len(triggers) > 0, 'Empty list of triggers'
    return TaskInfo(name,
                    triggers if isinstance(triggers, list) else [triggers],
                    run_at_start)
