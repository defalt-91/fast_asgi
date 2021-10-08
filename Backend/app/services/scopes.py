from typing import Dict, Literal, Optional

ScopeTypes = Literal["me", "posts", "items"]
all_scopes: Dict[ScopeTypes, str] = {
		"me"   : "Read information about the current user.",
		"posts": "Read Posts.",
		"users": "Read Posts.",
		"arman": "arman"
}
