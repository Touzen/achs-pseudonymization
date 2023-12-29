import re
import io

from zipfile import ZipFile
from pathlib import Path
from typing import List

from .representations import Document, Annotation

line_parser = re.compile(r"(T\d+)\t(\w+) (\d+) (\d+)\t(.+)")


def extract_ann(document: Document) -> str:
    ann_lines = []
    for idx, ann in enumerate(document.annotations):
        ann_lines.append(f'T{idx}\t{ann.label}\t{ann.start}\t{ann.end}\t{document.text[ann.start:ann.end]}')
    
    return '\n'.join(ann_lines)


def write_corpus(out_location: Path, documents: List[Document]):
    with ZipFile(out_location, 'w') as outzip:
        for doc in documents:
            with outzip.open(doc.filename, 'w') as f:
                f.write(extract_ann(doc).encode('utf-8'))
            with outzip.open(doc.filename.replace('.ann', '.txt'), 'w') as f:
                f.write(doc.text.encode('utf-8'))

def read_file(path: Path) -> Document:
    with open(path, "r") as f:
        annotations = []
        spans = []
        for line in f:
            if line.startswith("T") and ";" not in line:
                _, label, start, end, span = line_parser.findall(line.strip())[0]
                annotation = Annotation(int(start), int(end), label)
                annotations.append(annotation)
                spans.append(span)

    with io.open(path.with_suffix(".txt"), "rt", newline="") as f:
        text = f.read()

    return Document(path.parts[-1], text, annotations)


def read_corpus(corpus_location: Path) -> List[Document]:
    documents = []
    for path in corpus_location.glob("*.ann"):
        document = read_file(path)
        documents.append(document)

    return documents