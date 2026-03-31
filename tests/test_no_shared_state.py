"""DO NOT DELETE — Enforces that CvC agents have NO shared state.

Each agent MUST be fully independent. Agents may run in separate processes.
No shared dicts, objects, or communication between agents — ever.

This test exists because shared state has been accidentally introduced
multiple times. It MUST remain and pass at all times.
"""

import inspect
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add cogames to path so we can import cvc modules
_cogames_dir = str(Path(__file__).parent.parent / "cogs" / "cogames")
if _cogames_dir not in sys.path:
    sys.path.insert(0, _cogames_dir)


def _make_mock_policy_env_info():
    """Create a minimal mock PolicyEnvInterface for testing."""
    mock = MagicMock()
    mock.action_names = ["noop", "move_north", "move_south", "move_east", "move_west"]
    mock.vibe_action_names = ["change_vibe_miner", "change_vibe_aligner"]
    mock.obs_width = 13
    mock.obs_height = 13
    return mock


class TestNoSharedState:
    """DO NOT DELETE — Agents must be fully independent."""

    def _make_two_agents(self):
        """Create two agent GameStates via CvCPolicyImpl."""
        from cvc.cvc_policy import CvCPolicyImpl
        from cvc.programs import all_programs

        env = _make_mock_policy_env_info()
        programs = all_programs()

        impl0 = CvCPolicyImpl(env, agent_id=0, programs=programs)
        impl1 = CvCPolicyImpl(env, agent_id=1, programs=programs)

        state0 = impl0.initial_agent_state()
        state1 = impl1.initial_agent_state()

        return state0.game_state, state1.game_state

    def test_agents_have_independent_junctions(self):
        """Each agent's junction dict must be a SEPARATE object."""
        gs0, gs1 = self._make_two_agents()
        assert gs0.engine._junctions is not gs1.engine._junctions, (
            "AGENTS SHARE JUNCTION MEMORY! Each agent must have its own "
            "independent junction dict. Shared junctions are forbidden."
        )

    def test_agents_have_independent_claims(self):
        """Each agent's claims dict must be a SEPARATE object."""
        gs0, gs1 = self._make_two_agents()
        assert gs0.engine._claims is not gs1.engine._claims, (
            "AGENTS SHARE CLAIMS DICT! Each agent must have its own "
            "independent claims dict. Shared state is forbidden."
        )

    def test_agents_have_independent_world_models(self):
        """Each agent's world model must be a SEPARATE object."""
        gs0, gs1 = self._make_two_agents()
        assert gs0.engine._world_model is not gs1.engine._world_model, (
            "AGENTS SHARE WORLD MODEL! Each agent must have its own "
            "independent WorldModel instance."
        )

    def test_cvc_policy_no_shared_dicts(self):
        """CvCPolicy must NOT have shared junction/claims attributes."""
        from cvc.cvc_policy import CvCPolicy

        env = _make_mock_policy_env_info()
        policy = CvCPolicy(env)

        assert not hasattr(policy, '_shared_junctions'), (
            "CvCPolicy has _shared_junctions! No shared state — ever."
        )
        assert not hasattr(policy, '_shared_claims'), (
            "CvCPolicy has _shared_claims! No shared state — ever."
        )

    def test_game_state_no_shared_params(self):
        """GameState.__init__ must not accept shared_junctions/shared_claims."""
        from cvc.game_state import GameState

        sig = inspect.signature(GameState.__init__)
        params = set(sig.parameters.keys())

        assert 'shared_junctions' not in params, (
            "GameState accepts shared_junctions! No shared state."
        )
        assert 'shared_claims' not in params, (
            "GameState accepts shared_claims! No shared state."
        )

    def test_policy_impl_no_shared_params(self):
        """CvCPolicyImpl.__init__ must not accept shared_junctions/shared_claims."""
        from cvc.cvc_policy import CvCPolicyImpl

        sig = inspect.signature(CvCPolicyImpl.__init__)
        params = set(sig.parameters.keys())

        assert 'shared_junctions' not in params, (
            "CvCPolicyImpl accepts shared_junctions! No shared state."
        )
        assert 'shared_claims' not in params, (
            "CvCPolicyImpl accepts shared_claims! No shared state."
        )

    def test_mutation_does_not_leak(self):
        """Mutating one agent's junctions must not affect another's."""
        gs0, gs1 = self._make_two_agents()

        gs0.engine._junctions[(0, 0)] = ("team_a", 100)
        assert (0, 0) not in gs1.engine._junctions, (
            "Junction mutation leaked between agents! Dicts are shared."
        )

        gs0.engine._claims[(5, 5)] = (0, 50)
        assert (5, 5) not in gs1.engine._claims, (
            "Claims mutation leaked between agents! Dicts are shared."
        )
