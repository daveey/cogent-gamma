"""LearnerCoglet — receives aggregated loss signals and produces updates.

Listens on "signals" channel, calls the abstract learn() method,
and transmits the result on "update".
"""

from __future__ import annotations

from typing import Any

from coglet.coglet import Coglet, listen


class LearnerCoglet(Coglet):
    """Abstract base for learner coglets.

    Subclasses must implement learn(signals) -> update dict.
    """

    @listen("signals")
    async def _on_signals(self, signals: Any) -> None:
        result = await self.learn(signals)
        await self.transmit("update", result)

    async def learn(self, signals: Any) -> Any:
        raise NotImplementedError("Subclasses must implement learn()")
