import argparse
from pathlib import Path

from util.representations import Document, Annotation
from util.brat import write_corpus, read_corpus

import pseudonymizers
from pseudonymizers import pseudonymize

def pseudonymize_annotation(ann: Annotation, doc: Document) -> int:
    text = doc.text[ann.start:ann.end]
    replaced_text = pseudonymize(text, ann.label)

    delta = len(replaced_text) - len(text)

    doc.text = doc.text[:ann.start] + replaced_text + doc.text[ann.end:]
    ann.end += delta

    return delta

def pseudonymize_document(document: Document):
    offset = 0
    for ann in document.get_annotations():
        ann.start += offset
        ann.end += offset

        offset += pseudonymize_annotation(ann, document)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=Path)
    parser.add_argument('--out', '-o', dest='out', type=Path, required=False)
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', default=False)

    args = parser.parse_args()

    if args.verbose:
        pseudonymizers.CONFIG.debug = True

    out = args.out or Path(*args.path.parts[:-1], 'brat_pseudonymized_' + args.path.parts[-1] + '.zip')

    print(f'Loading documents from {args.path}.')
    documents = read_corpus(args.path)

    print(f'Pseudonymizing {len(documents)} documents.')
    for doc in documents:
        pseudonymize_document(doc)

    print(f'Saving documents to {out}.')
    write_corpus(out, documents)

