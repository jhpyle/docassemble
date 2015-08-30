#! /usr/bin/python
from docassemble import Interview

interview = Interview("tests/testinterview/questions.yml")
interview.assemble()
