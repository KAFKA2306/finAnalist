import io
import zipfile

from research.collect_openai_signals import collect


def test_collect_indexes_csv_without_interpreting_columns():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("usage.csv", "month,share\n2026-01,0.5\n2026-02,0.6\n")
        archive.writestr("README.txt", "ignored")
    result = collect(buffer.getvalue())
    assert result["publisher"] == "OpenAI"
    assert result["files"][0]["name"] == "usage.csv"
    assert result["files"][0]["rows"] == 2
    assert result["files"][0]["columns"] == ["month", "share"]
