from enum import Enum, IntEnum, auto
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union


class Events(Enum):
	USER_REGISTER = auto()
	PASSWORD_RESET = auto()
	USER_LOGIN = auto()
	REFRESH_TOKEN_GENERATE = auto()


DATA = TypeVar("DATA")
subscriptions: Dict[Events, Optional[List[Callable[[DATA], None]]]] = dict()


class EventException(Exception):
	"""exception for events that are not in Events Enum"""
	
	def __init__(self, e):
		self.msg = f"error: {e} ---, you need to register this event in event_types"


#  add itself to functions list of event_type
def subscribe(event_type: Events, func: Callable[..., None]):
	if event_type not in subscriptions:
		subscriptions[event_type] = []
	try:
		subscriptions[event_type].append(func)
	except KeyError as e:
		raise EventException(e)


#  execute all functions with data as function parameters
def post_event(event_type: Events, data: DATA, *args, **kwargs):
	if event_type not in subscriptions:
		return
	for func in subscriptions[event_type]:
		func(data)
