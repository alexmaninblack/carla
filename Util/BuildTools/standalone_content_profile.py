#!/usr/bin/env python3
"""Project a prop catalogue onto a deliberately limited cooked Game package.

Run after cooking and before package signing. Never edits source content or an
existing output. The exclusions report is required: this is a smaller supported
catalogue, not a repair of missing assets or a claim of full CARLA coverage.
"""
import argparse
import hashlib
import json
from pathlib import Path


def project_catalogue(catalogue, cooked):
    result = dict(catalogue)
    selected, excluded, seen = [], [], set()
    for prop in catalogue['Props']:
        name, mesh = prop['Name'], prop['Mesh']
        if name in seen or not mesh.startswith('/Game/') or '..' in mesh:
            raise ValueError('Invalid or repeated catalogue entry')
        seen.add(name)
        package = mesh.split('.', 1)[0]
        if package in cooked:
            selected.append(prop)
        else:
            excluded.append({'name': name, 'package': package})
    if not selected:
        raise ValueError('Empty catalogue is not a successful projection')
    result['Props'] = selected
    return result, excluded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalogue', type=Path, required=True)
    parser.add_argument('--cooked-content', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    source = args.catalogue.resolve(strict=True)
    content = args.cooked_content.resolve(strict=True)
    if not content.is_dir():
        parser.error('Cooked content must be a directory')
    output, report = args.output.absolute(), args.report.absolute()
    if output == report or output.exists() or report.exists():
        parser.error('Outputs must be distinct new files; existing data is preserved')
    if any(p.is_symlink() for p in content.rglob('*.uasset')):
        parser.error('Cooked package assets must not resolve to external source files')
    raw = source.read_bytes()
    catalogue = json.loads(raw)
    cooked = {'/Game/' + p.relative_to(content).with_suffix('').as_posix()
              for p in content.rglob('*.uasset')}
    projected, excluded = project_catalogue(catalogue, cooked)
    encoded = (json.dumps(projected, indent=2) + '\n').encode()
    manifest = {
        'profileKind': 'explicit-cooked-prop-subset',
        'sourceCatalogueSha256': hashlib.sha256(raw).hexdigest(),
        'outputCatalogueSha256': hashlib.sha256(encoded).hexdigest(),
        'sourceCount': len(catalogue['Props']),
        'includedCount': len(projected['Props']),
        'excluded': excluded,
        'sourceUnmodified': True,
        'scope': 'Prop catalogue only; map/vehicle/sensor qualification is separate',
    }
    # Exclusive opens remain authoritative even if a concurrent writer appears
    # after preflight. Preserve a partial output on failure for reconciliation.
    with report.open('x') as stream:
        json.dump(manifest, stream, indent=2)
        stream.write('\n')
    with output.open('xb') as stream:
        stream.write(encoded)
    print(json.dumps({'includedCount': manifest['includedCount'],
                      'excludedCount': len(excluded)}))


if __name__ == '__main__':
    main()
