from typing import Dict, Literal, Optional

ScopeTypes = Literal["me", "posts", "items"]
all_scopes: Dict[ScopeTypes, str] = {
	"me": "Read information about the current user.",
	"users": "Read Posts.",
	"posts": "Read Write Posts"
}
