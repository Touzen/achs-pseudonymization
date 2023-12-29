import re
from dataclasses import dataclass
from typing import List, Iterator

splitter = re.compile(r'\w+|[^\s\w]|@+')

ENTITY_CLASSES = ["Age", "Company", "Health_Care_Unit", "Date_Part", "Full_Date", "First_Name", "Last_Name", "Location", "Occupation", "Phone_Number", "RUT"]

@dataclass
class Annotation:
    start: int
    end: int
    label: str

@dataclass
class Span:
    text: str
    label: str

@dataclass
class Document:
    filename: str
    text: str
    annotations: List[Annotation]
    zero_label: str = 'O'

    def get_spans(self) -> Iterator[Span]: 
        annotations = sorted(self.annotations, key=lambda a: a.start)

        pointer = 0
        for ann in annotations:
            zero_text = self.text[pointer:ann.start]
            yield Span(zero_text, self.zero_label)

            labeled_text = self.text[ann.start:ann.end]
            yield Span(labeled_text, ann.label)

            pointer = ann.end

        remainder = self.text[pointer:]
        yield Span(remainder, self.zero_label)

    def get_annotations(self) -> Iterator[Annotation]:
        annotations = sorted(self.annotations, key=lambda a: a.start)
        for ann in annotations:
            yield ann
