from csv import DictWriter
import io
from typing import Dict, List, Iterable


def write_dict_as_csv(rows: List[Dict], fieldnames: Iterable[str], **kwargs):
    writer_file = io.StringIO()
    writer = DictWriter(writer_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rowdicts=rows)
    bio = io.BytesIO(writer_file.getvalue().encode("utf-8"))
    bio.seek(0)
    return bio
