"""The font is a set of named geometric templates at measured design locations.

Measurements are prepared separately. Building never needs the reference font.
Unknown characters and unmeasured instances fail instead of using font fallback.
"""
from dataclasses import dataclass
import json
from pathlib import Path
from fontTools.pens.transformPen import TransformPen

from font_recovery.primitives import draw_template

DESIGN = Path(__file__).with_name('data') / 'design.json'


def require_alphabet(models):
    """Fail before emitting fonts if a master is missing a requested letter."""
    required = json.loads((DESIGN.parent / 'required-alphabet.json').read_text())
    for model in models:
        missing = [row['character'] for row in required if row['character'] not in model.glyphs]
        if missing:
            raise ValueError(f"Incomplete alphabet at {model.location}: {''.join(missing)}")


@dataclass(frozen=True)
class FontModel:
    location: dict[str, float]
    glyphs: dict[str, dict]
    units_per_em: int = 2048

    @classmethod
    def load_all(cls, path: Path = DESIGN) -> list['FontModel']:
        data = json.loads(path.read_text())
        return [cls(**sample) for sample in data['samples']]

    def draw(self, character: str, pen) -> None:
        """Construct the character from dimensions and curve parameters."""
        parameters = self.glyphs[character]
        if parameters['template'] == 'skeleton':
            from font_recovery.alphabet import draw_skeleton
            draw_skeleton(pen, character, parameters)
        elif parameters['template'] == 'accented':
            from font_recovery.alphabet import draw_accent
            shift = (1, 0, 0, 1, parameters['dx'], 0)
            self.draw(parameters['base'], TransformPen(pen, shift))
            draw_accent(pen, parameters)
        elif parameters['template'] == 'component':
            # Related alphabets can share a shape while retaining their own
            # measured bearings. This does not substitute Cyrillic topology.
            shift = (1, 0, 0, 1, parameters['dx'], parameters.get('dy', 0))
            self.draw(parameters['base'], TransformPen(pen, shift))
        else:
            draw_template(pen, character, parameters)

    def advance(self, character: str) -> int:
        return round(self.glyphs[character]['advance'])


def export_design(measurements: Path, output: Path = DESIGN) -> None:
    """Keep generation parameters in source; leave fitting evidence in build/."""
    data = json.loads(measurements.read_text())
    evidence = {'observed_moments', 'model_moments', 'fit_residual_norm',
                'observed_scan_features'}

    def parameters(value):
        if isinstance(value, dict):
            return {key: parameters(item) for key, item in value.items()
                    if key not in evidence}
        if isinstance(value, list):
            return [parameters(item) for item in value]
        return value

    design = {
        'family': 'Tabuna Sans',
        'status': 'development; incomplete alphabet',
        'units_per_em': 2048,
        'samples': parameters(data['samples']),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(design, ensure_ascii=False, indent=2) + '\n')
