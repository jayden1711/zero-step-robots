"""Modified-physics variants. Each is the stock Gymnasium MuJoCo XML with one text substitution, so published
gains tuned on the stock models should not transfer exactly. Observation/action spaces, reward, termination
thresholds and episode length are unchanged. The default (variant=None) is the stock model."""
import tempfile
from pathlib import Path

import gymnasium
import mujoco  # noqa: F401  (import check: variants need the same MuJoCo the envs use)

ASSETS = Path(gymnasium.__file__).parent / "envs" / "mujoco" / "assets"
XML = {"cartpole": "inverted_pendulum.xml", "hopper": "hopper.xml"}

# (old text, new text) substitutions on the stock XML. Mass changes use a geom density (stock density is 1000).
VARIANTS = {
    "cartpole": {
        "pole_long": [('fromto="0 0 0 0.001 0 0.6" name="cpole" rgba="0 0.7 0.7 1" size="0.049 0.3"',
                       'fromto="0 0 0 0.001 0 1.2" name="cpole" rgba="0 0.7 0.7 1" size="0.049 0.6"')],
        "pole_heavy": [('name="cpole" rgba', 'name="cpole" density="3000" rgba')],
        "gravity_low": [('gravity="0 0 -9.81"', 'gravity="0 0 -4.905"')],
        "gravity_high": [('gravity="0 0 -9.81"', 'gravity="0 0 -19.62"')],
    },
    "hopper": {
        "torso_heavy": [('name="torso_geom"', 'name="torso_geom" density="2000"')],
        "torso_light": [('name="torso_geom"', 'name="torso_geom" density="500"')],
    },
}


def variant_names(task: str) -> list:
    return list(VARIANTS[task])


def variant_xml_path(task: str, variant: str) -> str:
    text = (ASSETS / XML[task]).read_text()
    for old, new in VARIANTS[task][variant]:
        if text.count(old) != 1:
            raise ValueError(f"{task}/{variant}: pattern {old!r} found {text.count(old)} times in stock XML")
        text = text.replace(old, new)
    d = Path(tempfile.gettempdir()) / "zsr_variants"
    d.mkdir(exist_ok=True)
    p = d / f"{task}_{variant}.xml"
    p.write_text(text)
    return str(p)
