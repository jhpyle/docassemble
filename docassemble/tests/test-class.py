from origclass import Food

class Food(Food):
    def eat(self):
        print "I ate " + str(self.describe())

apple = Food()
apple.eat()
