import pytest

from data.verify import check_files, sha256_of

REQUIRED = "cira/required.zip"
OPTIONAL = "cira/optional.zip"


@pytest.fixture
def raw_dir(tmp_path):
    """Pasta de dados com um arquivo obrigatório e um opcional."""
    (tmp_path / "cira").mkdir()
    (tmp_path / REQUIRED).write_bytes(b"conteudo obrigatorio")
    (tmp_path / OPTIONAL).write_bytes(b"conteudo opcional")
    return tmp_path


@pytest.fixture
def manifest(raw_dir):
    """Manifesto com os hashes dos arquivos como estão em `raw_dir`."""
    return {
        "files": [
            {"path": REQUIRED, "sha256": sha256_of(raw_dir / REQUIRED), "required": True},
            {"path": OPTIONAL, "sha256": sha256_of(raw_dir / OPTIONAL), "required": False},
        ]
    }


def test_check_passes_when_hashes_match(manifest, raw_dir):
    assert check_files(manifest, raw_dir) == ([], [])


def test_changed_file_is_an_error_that_names_the_file(manifest, raw_dir):
    (raw_dir / REQUIRED).write_bytes(b"conteudo alterado")

    errors, warnings = check_files(manifest, raw_dir)

    assert len(errors) == 1
    assert "divergente" in errors[0]
    assert REQUIRED in errors[0]
    assert warnings == []


def test_missing_required_file_is_an_error_that_names_the_file(manifest, raw_dir):
    (raw_dir / REQUIRED).unlink()

    errors, warnings = check_files(manifest, raw_dir)

    assert len(errors) == 1
    assert "ausente" in errors[0]
    assert REQUIRED in errors[0]
    assert warnings == []


def test_missing_optional_file_is_only_a_warning(manifest, raw_dir):
    (raw_dir / OPTIONAL).unlink()

    errors, warnings = check_files(manifest, raw_dir)

    assert errors == []
    assert len(warnings) == 1
    assert OPTIONAL in warnings[0]
