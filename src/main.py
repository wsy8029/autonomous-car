from autonomous_car import AutonomousCar

def main():
    with AutonomousCar() as car:
        car.run()

if __name__ == '__main__':
    main()