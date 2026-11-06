from pathlib import Path

import pytest

from assistant_core.errors import DataError
from assistant_core.knowledge import Handbook, OfficeDirectory

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# --- OfficeDirectory Tests ---


def test_office_directory_from_csv():
    directory = OfficeDirectory.from_csv(DATA_DIR / "offices.csv")
    assert "library" in directory.names
    assert "training office" in directory.names

    office = directory.find("Where is the library?")
    assert office is not None
    assert office.name == "Library"
    assert office.room == "B.201"
    assert office.hours == "Mon-Sat 07:00-20:00"


def test_office_directory_find_case_insensitive():
    directory = OfficeDirectory.from_csv(DATA_DIR / "offices.csv")
    office = directory.find("need help from IT HELPDESK please")
    assert office is not None
    assert office.name == "IT Helpdesk"


def test_office_directory_find_vietnamese_and_abbreviation_aliases():
    directory = OfficeDirectory.from_csv(DATA_DIR / "offices.csv")
    # Accented Vietnamese
    assert directory.find("phòng đào tạo ở đâu vậy?") == directory.find("Training Office")
    assert directory.find("thư viện mở cửa khi nào") == directory.find("Library")
    assert directory.find("liên hệ công nghệ thông tin") == directory.find("IT Helpdesk")
    assert directory.find("công tác sinh viên") == directory.find("Student Affairs")
    # Unaccented Vietnamese
    assert directory.find("phong dao tao o dau") == directory.find("Training Office")
    assert directory.find("thu vien o dau") == directory.find("Library")
    assert directory.find("cong nghe thong tin") == directory.find("IT Helpdesk")
    assert directory.find("cong tac sinh vien") == directory.find("Student Affairs")
    # Abbreviations with word boundaries
    assert directory.find("cho mình hỏi pdt") == directory.find("Training Office")
    assert directory.find("pdt ở phòng nào") == directory.find("Training Office")
    assert directory.find("liên hệ ctsv") == directory.find("Student Affairs")


def test_office_directory_find_short_alias_word_boundary_isolation():
    """Verify that short aliases like 'pdt' do not trigger false-positive matches inside words like 'update'."""
    directory = OfficeDirectory.from_csv(DATA_DIR / "offices.csv")
    assert directory.find("cần update thông tin môn học") is None
    assert directory.find("vui lòng update lịch thi") is None


def test_office_directory_find_empty_and_unmatched():
    directory = OfficeDirectory.from_csv(DATA_DIR / "offices.csv")
    assert directory.find("") is None
    assert directory.find("   ") is None
    assert directory.find("Where is the cafeteria?") is None
    assert directory.find("tuition for 18 credits") is None


def test_office_directory_find_miss():
    directory = OfficeDirectory.from_csv(DATA_DIR / "offices.csv")
    assert directory.find("Where is the cafeteria?") is None


def test_office_directory_all():
    directory = OfficeDirectory.from_csv(DATA_DIR / "offices.csv")
    offices = directory.all()
    assert len(offices) == 4
    names = [o.name for o in offices]
    assert names == ["IT Helpdesk", "Library", "Student Affairs", "Training Office"]
    assert names == sorted(names)


def test_office_directory_all_empty():
    directory = OfficeDirectory({})
    assert directory.all() == []


def test_office_directory_missing_file(tmp_path):
    with pytest.raises(DataError):
        OfficeDirectory.from_csv(tmp_path / "nonexistent.csv")


def test_office_directory_malformed_csv(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("invalid,header\nfoo,bar\n", encoding="utf-8")
    with pytest.raises(DataError):
        OfficeDirectory.from_csv(bad_csv)


def test_office_directory_missing_column(tmp_path):
    bad_csv = tmp_path / "missing_col.csv"
    bad_csv.write_text("name,room,hours\nOffice 1,A.101\n", encoding="utf-8")
    with pytest.raises(DataError):
        OfficeDirectory.from_csv(bad_csv)


# --- Handbook Tests ---


def test_handbook_from_json():
    handbook = Handbook.from_json(DATA_DIR / "handbook.json")

    rule = handbook.search("can I register my thesis with 118 credits")
    assert rule is not None
    assert rule.id == "H26-5.3"
    assert rule.title == "Thesis registration"


def test_handbook_search_retake():
    handbook = Handbook.from_json(DATA_DIR / "handbook.json")
    rule = handbook.search("how do I retake a failed course?")
    assert rule is not None
    assert rule.id == "H26-4.2"


def test_handbook_search_exam_absence():
    handbook = Handbook.from_json(DATA_DIR / "handbook.json")
    rule = handbook.search("medical exam absence policy")
    assert rule is not None
    assert rule.id == "H26-7.2"


def test_handbook_search_miss():
    handbook = Handbook.from_json(DATA_DIR / "handbook.json")
    assert handbook.search("what is the weather today in Hanoi?") is None


def test_handbook_search_short_words_only():
    handbook = Handbook.from_json(DATA_DIR / "handbook.json")
    # All words <= 3 chars: no keyword should match
    assert handbook.search("hi is it ok") is None


def test_handbook_missing_file(tmp_path):
    with pytest.raises(DataError):
        Handbook.from_json(tmp_path / "nonexistent.json")


def test_handbook_malformed_json_syntax(tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(DataError):
        Handbook.from_json(bad_json)


def test_handbook_malformed_json_structure(tmp_path):
    bad_json = tmp_path / "bad_structure.json"
    bad_json.write_text(r'[{"id": "1", "title": "Missing text"}]', encoding="utf-8")
    with pytest.raises(DataError):
        Handbook.from_json(bad_json)
