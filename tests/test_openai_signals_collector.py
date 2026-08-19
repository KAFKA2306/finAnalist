import io
import unittest
import zipfile

from research.collect_openai_signals import collect


class OpenAISignalsCollectorTest(unittest.TestCase):
    def test_collect_indexes_csv_without_interpreting_columns(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("usage.csv", "month,share\n2026-01,0.5\n2026-02,0.6\n")
            archive.writestr("README.txt", "ignored")

        result = collect(buffer.getvalue())

        self.assertEqual(result["publisher"], "OpenAI")
        self.assertEqual(result["files"][0]["name"], "usage.csv")
        self.assertEqual(result["files"][0]["rows"], 2)
        self.assertEqual(result["files"][0]["columns"], ["month", "share"])
        self.assertEqual(result["files"][0]["encoding"], "utf-8-sig")

    def test_collect_preserves_hash_for_non_utf8_csv(self):
        buffer = io.BytesIO()
        csv_bytes = "label,value\nCaf\u00e9,1\n".encode("cp1252")
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("usage.csv", csv_bytes)

        result = collect(buffer.getvalue())
        item = result["files"][0]
        self.assertEqual(item["encoding"], "cp1252")
        self.assertEqual(item["columns"], ["label", "value"])
        self.assertEqual(item["rows"], 1)
        self.assertEqual(item["bytes"], len(csv_bytes))
        self.assertEqual(len(item["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
