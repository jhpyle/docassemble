from docassemble.base.util import Thing, Person, Individual, DAList, DAObject, Organization


__all__ = ['Situation']


class Entity(Organization):
    pass


class Representative(Person):
    pass


class CorporateDirector(Organization):
    pass


class EntityList(DAList):
    def init(self, *pargs, **kwargs):
        self.object_type = Entity
        self.complete_attribute = 'complete'
        self.gathered = True
        super().init(*pargs, **kwargs)


class RepresentativeList(DAList):
    def init(self, *pargs, **kwargs):
        self.object_type = Representative
        self.complete_attribute = 'complete'
        self.gathered = True
        super().init(*pargs, **kwargs)


class CorporateDirectorList(DAList):
    def init(self, *pargs, **kwargs):
        self.object_type = CorporateDirector
        self.complete_attribute = 'complete'
        self.gathered = True
        super().init(*pargs, **kwargs)


class Situation(DAObject):
    def init(self, *pargs, **kwargs):
        self.initializeAttribute('entities', EntityList)
        self.initializeAttribute('representatives', RepresentativeList)
        self.initializeAttribute('corporate_directors', CorporateDirectorList)
        self.reconciling = False
        super().init(*pargs, **kwargs)

    def directors_of_entity(self, entity):
        return [director for director in self.corporate_directors if entity in director.directing]

    def people_related_to_entity(self, entity):
        people = set()
        people.update(self.directors_of_entity(entity))
        for representative in self.representatives:
            for client in representative.representing:
                if client is entity or client in people:
                    people.add(representative)
        return list(people)

    def representives_of(self, client):
        return [representative for representative in self.representatives if client in representative.representing]

    def reconcile(self):
        if self.reconciling:
            return
        self.reconciling = True
        for director in self.corporate_directors:
            to_remove = []
            for entity in director.directing:
                if entity not in self.entities:
                    to_remove.append(entity)
            for entity in to_remove:
                director.directing.remove(entity)
        for representative in self.representatives:
            to_remove = []
            for client in representative.representing:
                if not (client in self.entities or client in self.corporate_directors):
                    to_remove.append(client)
            for client in to_remove:
                representative.representing.remove(client)
        self.reconciling = False
