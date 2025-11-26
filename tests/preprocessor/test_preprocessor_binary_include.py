import os
import sys

# Make sure repository root is on sys.path so tests can import `src` package
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.compiler.preprocessor import Preprocessor


def test_binary_include_embedded(tmp_path):
    # Arrange: use the existing Bubble_Ordering.txt which includes Bubble_Ordering_func_.txt
    tests_dir = os.path.join(os.path.dirname(__file__))
    input_file = os.path.join(tests_dir, 'Bubble_Ordering.txt')

    pre = Preprocessor()

    # Act: preprocess the file
    result = pre.preprocess_file(input_file)

    # Assert: preprocessor returns bytes and binary include was inlined verbatim
    assert isinstance(result, (bytes, bytearray))

    expected_bin_path = os.path.join(tests_dir, 'Bubble_Ordering_func_.bin')
    with open(expected_bin_path, 'rb') as bf:
        expected_bytes = bf.read()

    # The binary contents should appear inside the resulting bytes stream
    assert expected_bytes in result

    # Also check the CLI helper writes a .bin output file when binary content is returned
    out_dir = tmp_path / 'out'
    out_dir.mkdir()
    from src.compiler.preprocessor import preprocess_file_cli

    out_path = preprocess_file_cli(input_file, str(out_dir))
    assert out_path.endswith('_preprocessed.bin')
    with open(out_path, 'rb') as of:
        on_disk = of.read()
    assert on_disk == result
