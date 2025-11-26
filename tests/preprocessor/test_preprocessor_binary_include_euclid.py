import os
import sys

# Make sure repository root is on sys.path so tests can import `src` package
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.compiler.preprocessor import Preprocessor, preprocess_file_cli


def test_euclid_binary_inlined(tmp_path):
    tests_dir = os.path.join(os.path.dirname(__file__))
    input_file = os.path.join(tests_dir, 'Euclidean_Algorithm.txt')

    pre = Preprocessor()
    result = pre.preprocess_file(input_file)

    # Should return bytes because the include has a .bin counterpart
    assert isinstance(result, (bytes, bytearray))

    expected_bin_path = os.path.join(tests_dir, 'Euclidean_Algorithm_maxcd.bin')
    with open(expected_bin_path, 'rb') as bf:
        expected_bytes = bf.read()

    assert expected_bytes in result

    # CLI should write a .bin file and equal content
    out_dir = tmp_path / 'out'
    out_dir.mkdir()
    out_path = preprocess_file_cli(input_file, str(out_dir))
    assert out_path.endswith('_preprocessed.bin')
    with open(out_path, 'rb') as of:
        on_disk = of.read()
    assert on_disk == result
