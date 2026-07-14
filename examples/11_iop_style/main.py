"""IOP-style Example — Native Intent-based approach.

Flow:
  1. Define Intent explicitly (user creates Intent data)
  2. Define handler (pure function)
  3. Register Intent + handler
  4. Ready to execute

User has full control over Intent creation.
"""

import asyncio

from evoid.core import Intent, Level, Context
from evoid.web.iop_style import create_service, on, run
from evoid.engines.logger import loguru as log
from evoid.core import all_intents, all_processors


# Create service
app = create_service("my-api")

# 1. Define Intents (EXPLICIT — user creates them)
GET_USER = Intent(name="get_user", level=Level.STANDARD)
CREATE_USER = Intent(name="create_user", level=Level.STANDARD)
HEALTH = Intent(name="health", level=Level.EPHEMERAL)


# 2. Define handlers (pure functions)
async def get_user(intent: Intent) -> dict:
    user_id = intent.metadata.get("user_id", 0)
    log.info(f"Getting user {user_id}")
    return {"id": user_id, "name": f"User {user_id}"}


async def create_user(intent: Intent) -> dict:
    data = intent.metadata.get("body", {})
    log.info(f"Creating user: {data}")
    return {"status": "created", "user": data}


async def health(intent: Intent) -> dict:
    return {"status": "healthy"}


# 3. Register Intent + handler
on(app, GET_USER, get_user)
on(app, CREATE_USER, create_user)
on(app, HEALTH, health)


# Show what was registered
print("Registered Intents:")
for name, intent in all_intents().items():
    print(f"  {name} [{intent.level.value}]")

print("\nRegistered Processors:")
for name in all_processors():
    print(f"  {name}")


# Run
if __name__ == "__main__":
    log.init("evoid-iop", level="INFO")
    asyncio.run(run(app, port=8000))
