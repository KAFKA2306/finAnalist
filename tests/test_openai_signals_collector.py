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


if __name__ == "__main__":
    unittest.main()
