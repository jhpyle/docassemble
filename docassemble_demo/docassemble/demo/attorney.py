from docassemble.base.legal import Individual, objects_from_file

organizations = objects_from_file('docassemble.demo:data/objects/organizations.yml')

def organizations_handling(problem=None, county=None):
    response = list()
    for organization in organizations:
        if organization.will_handle(problem=problem, county=county):
            response.append(organization)
    return response

def problem_types():
    response = list()
    for organization in organizations:
        if hasattr(organization, 'handles'):
            for problem in organization.handles:
                if problem not in response:
                    response.append(problem)
    return sorted(response)

class Attorney(Individual):
    def can_practice_in(self, state):
        if state in self.bar_admissions and self.bar_admissions[state] is True:
            return True
        return False
