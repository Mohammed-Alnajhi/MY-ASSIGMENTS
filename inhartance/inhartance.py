class Father:
    def skills_father(self):
        print("Driving")

class Mother:
    def skills_mother(self):
        print("Cooking")

class Child(Father, Mother):
    pass


c = Child()

c.skills_father()
c.skills_mother()
