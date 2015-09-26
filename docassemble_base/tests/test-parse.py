import os
import sys

from docassemble.base.interview_cache import get_interview
from docassemble.base.parse import InterviewStatus

package_path = os.path.join(os.path.expanduser("~"), 'docassemble')

questionFile = os.path.join(package_path, 'docassemble_demo', 'docassemble', 'demo', 'data', 'questions', 'questions.yml')

interview = get_interview(questionFile)

user_dict = {'user_has_injury': True}
interview_status = InterviewStatus()

user_dict = interview.assemble(user_dict, interview_status)


