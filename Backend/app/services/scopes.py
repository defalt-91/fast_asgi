from typing import Dict, Literal


ScopeTypes = Literal["me", "posts", "items", "admin"]
all_scopes: Dict[ScopeTypes, str] = {
	"me": "Read information about the current user.",
	"posts": "Read Write Posts",
	"admin": "Admin privileges",
}
