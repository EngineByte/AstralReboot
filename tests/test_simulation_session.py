import logging
import pytest

from astralengine.app.startup import ApplicationContext
from astralengine.bootstrap.application import ApplicationConfig
from astralengine.bootstrap.simulation import build_simulation_session
from astralengine.resources.scenes import SceneBootstrapState
from astralengine.resources.time import FrameClock
from astralengine.runtime.simulation_runner import SimulationRunner


pytestmark = [
    pytest.mark.integration,
    pytest.mark.simulation,
    pytest.mark.ecs
]


def test_simulation_session_builds() -> None:
    context = ApplicationContext(logger=None, debug=False, headless=True)  # replace with real logger if needed
    session = build_simulation_session(
        context=context,
        config=ApplicationConfig(max_frames=3, target_fps=None),
    )

    assert session.world is not None
    assert session.world.get_resource(FrameClock) is not None
    assert session.world.get_resource(SceneBootstrapState) is not None

def test_simulation_session_entities_expire_after_lifetime() -> None:
    context = ApplicationContext(
        logger=logging.getLogger("test.simulation"),
        debug=False,
        headless=True,
    )

    session = build_simulation_session(
        context=context,
        config=ApplicationConfig(
            fixed_dt=1.0 / 60.0,
            max_frames=None,
            target_fps=None,
        ),
    )

    runner = SimulationRunner(session)

    # Startup should spawn the initial test scene.
    runner.startup()
    assert session.world.entity_count() == 100

    # Run long enough for 5.0-second lifetimes to expire and be committed.
    for _ in range(420):
        runner.run_one_frame()

    assert session.world.entity_count() == 0

    runner.shutdown()