#! /usr/bin/python
from docassemble import Interview

interview = Interview("tests/testinterview/questions.yaml")
interview.assemble()
