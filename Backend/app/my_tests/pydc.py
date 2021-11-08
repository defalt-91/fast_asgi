import datetime
import datetime as dt
import os
import random
import time
from dataclasses import dataclass, field
from typing import Optional

import pydantic.dataclasses as pydc
from pydantic import BaseModel
from pydantic import Field


@dataclass
class DTToken:
	token_type: str
	token: str = field(default_factory=lambda: random.random())
	expires: dt.datetime = field(default_factory=lambda: dt.datetime.utcnow().timestamp())


class PDCToken(BaseModel):
	token_type: Optional[str]
	token: Optional[str] = Field(default_factory=lambda: random.random())
	expires: Optional[dt.datetime] = Field(default_factory=lambda: dt.datetime.utcnow().timestamp())


# @validator("expires", pre=True)
# def root_data(cls, v):
# 	v = now
# 	return v
#
# @validator("token", pre=True)
# def root_data2(cls, v):
# 	v = rand
# 	return v

@pydc.dataclass
class PYDCToken:
	token_type: str
	token: str = Field(default_factory=lambda: random.random())
	expires: dt.datetime = Field(default_factory=lambda: dt.datetime.utcnow().timestamp())


if __name__ == '__main__':
	before = datetime.datetime.now()
	func_lists = []
	for i in range(1000010):
		j = PDCToken(token_type="access_token")
		func_lists.append(j)
	after = datetime.datetime.now()
	print(time.process_time())
	print((after - before).total_seconds())
