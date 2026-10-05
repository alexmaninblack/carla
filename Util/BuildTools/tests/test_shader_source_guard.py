"""Small source-guard regression; runtime rendering needs packaged-game proof."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / 'Unreal/CarlaUnreal/Plugins/Carla/Source/Carla/Carla.cpp'


class ShaderSourceRegistrationTest(unittest.TestCase):
    def test_actual_early_guard_all_four_platform_modes(self):
        source = MODULE.read_text()
        match = re.search(r'void FCarlaModule::AddShaderSearchPaths\(\)\s*\{(.*?)'
                          r'// The shader virtual path', source, re.S)
        self.assertIsNotNone(match, 'Registration eligibility must precede source-directory access')
        # Compile the actual early function body, not a reimplementation of its
        # condition. Only platform inputs are stubbed; Unreal rendering remains
        # separately covered by the packaged-game integration test.
        program = '''
bool cooked, compiling;
int sourceRegistrationReached;
struct FPlatformProperties { static bool RequiresCookedData() { return cooked; } };
bool AllowShaderCompiling() { return compiling; }
void registration() {
''' + match.group(1) + '''
  ++sourceRegistrationReached;
}
int main() {
  for (int mode = 0; mode != 4; ++mode) {
    cooked = (mode & 1) != 0;
    compiling = (mode & 2) != 0;
    sourceRegistrationReached = 0;
    registration();
    if (sourceRegistrationReached != (mode == 2 ? 1 : 0)) return mode + 1;
  }
}
'''
        with tempfile.TemporaryDirectory(prefix='carla-shader-guard-') as directory:
            executable = Path(directory) / 'guard'
            compiler = shlex.split(os.environ.get('CXX', 'c++'))
            compiled = subprocess.run([*compiler, '-std=c++17', '-x', 'c++', '-', '-o', str(executable)],
                                      input=program, text=True, capture_output=True, timeout=30)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            checked = subprocess.run([str(executable)], capture_output=True, timeout=5)
            self.assertEqual(checked.returncode, 0)

    def test_uncooked_diagnostics_and_duplicate_mapping_guard_remain(self):
        source = MODULE.read_text()
        self.assertIn('AllShaderSourceDirectoryMappings().Contains(TEXT("/Plugin/Carla"))', source)
        self.assertIn('if (!FPaths::DirectoryExists(ShadersDirectoryPath))', source)
        self.assertIn('AddShaderSearchPaths: shader directory', source)
        self.assertLess(source.index('RequiresCookedData()'), source.index('FindPlugin(TEXT("Carla"))'))


if __name__ == '__main__':
    unittest.main()
