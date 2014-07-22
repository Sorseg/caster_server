import model


def main():
    model.Creature.create(user="Sorseg", name="Brohogol", pos_x=500, pos_y=500, type=1,
                          hp=50, max_hp=50)


if __name__ == '__main__':
    main()