import os
import sys

from docassemble.base.interview_cache import get_interview
from docassemble.base.parse import InterviewStatus

package_path = os.path.join(os.path.expanduser("~"), 'docassemble')

questionFile = os.path.join(package_path, 'docassemble-demo', 'docassemble', 'demo', 'data', 'questions', 'questions.yml')

interview = get_interview(questionFile)

user_dict = {'user_has_injury': True}
interview_status = InterviewStatus()

user_dict = interview.assemble(user_dict, interview_status)

exec('user_is_plaintiff = False', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

exec('case.plaintiff[i].name.first = "Jonathan"', user_dict)
exec('case.plaintiff[i].name.last = "Pyle"', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

exec('case.plaintiff.there_is_another = False', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

exec('user_is_defendant = True', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

sys.exit();

exec('user_has_children = True', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

exec('user.child[i].name.first = "Katy"', user_dict)
exec('user.child[i].name.last = "Bean"', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

exec('user_has_other_children = True', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

exec('user.child[i].name.first = "Billy"', user_dict)
exec('user.child[i].name.last = "Bean"', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

exec('user_has_other_children = False', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

exec('user.name.first = "Jill"', user_dict)
exec('user.name.last = "Bean"', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

exec('case.plaintiff.there_is_another = True', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

exec('case.plaintiff[i].name.first = "Jonathan"', user_dict)
exec('case.plaintiff[i].name.last = "Pyle"', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

exec('case.plaintiff.there_is_another = False', user_dict)

user_dict = interview.assemble(user_dict, interview_status)

#for key in user_dict:
#    print key, type(user_dict[key])

