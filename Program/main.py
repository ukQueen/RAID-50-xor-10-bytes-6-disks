import os

disks = ['disk_0.txt', 'disk_1.txt', 'disk_2.txt', 'disk_3.txt', 'disk_4.txt', 'disk_5.txt']

RAID_5_1 = ['disk_0.txt', 'disk_1.txt', 'disk_2.txt']
RAID_5_2 = ['disk_3.txt', 'disk_4.txt', 'disk_5.txt']
index_of_disk = []


def xor(a: str, b: str) -> str:
    return ''.join([chr(ord(x) ^ ord(y)) for x, y in zip(a, b)])


def recovery(disks_index: int) -> None:
    global index_of_disk
    global RAID_5_1
    global RAID_5_2

    if disks_index < 3:
        problem_raid = RAID_5_1
        problem_index = disks_index
    else:
        problem_raid = RAID_5_2
        problem_index = disks_index - 3

    lost_data = []
    data = []
    for i in range(len(problem_raid)):
        if i != problem_index:
            with open(problem_raid[i], 'r') as file:
                data.append([x for x in file.readlines() if x != '_\n'])
        else:
            data.append(["*" * 3] * 64)

    if data[0][0] != "***":
        cond = data[0]
    else:
        cond = data[1]
    for i in range(len(cond)):
        disk_data = []
        for j in range(len(data)):
            disk_data.append(data[j][i][:3])

        indexes = [ind for ind in range(len(disk_data)) if disk_data[ind] != "***"]

        if len(indexes) == 2:
            a = disk_data[indexes[0]]
            b = disk_data[indexes[1]]
            buf = xor(disk_data[indexes[0]], disk_data[indexes[1]])
            lost_data.append(buf)

    ind = 0
    with open(disks[disks_index], 'w') as file:
        for i in range(64):
            if i in index_of_disk:
                file.write(lost_data[ind] + '\n')
                ind += 1
            else:
                file.write("_\n")

    print("Диск {} был восстановлен.".format(disks_index))


def check_disks():
    disk_indexes = []
    can_recovery = True
    for i in range(len(disks)):
        if not os.path.isfile(disks[i]):
            disk_indexes.append(i)

    if len(disk_indexes) == 2:
        if not ((0 <= disk_indexes[0] <= 2 and 3 <= disk_indexes[1] <= 5) or
                (0 <= disk_indexes[1] <= 2 and 3 <= disk_indexes[0] <= 5)):
            can_recovery = False
    elif len(disk_indexes) > 2:
        can_recovery = False

    if can_recovery:
        for disk in disk_indexes:
            print("\nДиск {} отсутствовал.".format(disk))
            recovery(disk)
    else:
        output = "\nДиски "
        for i in range(len(disk_indexes)):
            output += str(disk_indexes[i])
            if i < len(disk_indexes) - 1:
                output += ', '

        output += " отсутсвуют"
        print(output)
        print("\nДиски с данными невозможно востановить")
        return "Данные невозможно востановить"


def read() -> None:
    global index_of_disk
    if len(index_of_disk) == 0:
        print('\nДиски пусты.\n')
        return

    if check_disks() != "Данные невозможно востановить":
        while True:
            index = input("\nВведите индекс строки которую хотите прочитать [0;63]: ")
            if int(index) > 63 or int(index) < 0:
                print("индекс вне диапазона [0;63].")
            elif int(index) not in index_of_disk:
                print("Данных нет по данному адресу.")
            else:
                break

        data = []

        for i in range(len(disks)):
            file = open(disks[i], 'r')
            data += [file.readlines()]
            file.close()

        result = ''
        index = int(index)
        for i in range(len(data)):
            if int(index % 3) != int(i % 3):
                if len(data[i][int(index)][:-1]) == 3:
                    buf = str(data[i][int(index)][:-1])

                    if ''.join(chr(0)) in buf:
                        buf = buf.replace(''.join(chr(0)), '')
                    result += buf
                else:
                    if i < len(data)//2:
                        indexes = [ind for ind in range(len(data)//2) if ind != int(index % 3) and ind != i]
                        recover_string = data[int(index % 3)][index]
                    else:
                        indexes = [ind for ind in range(len(data)//2, len(data)) if ind != int(index % 3) + 3 and ind != i]
                        recover_string = data[int(index % 3) + 3][index]
                    result += xor(data[indexes[0]], recover_string)

        print("Данные по адресу {}: ".format(index))
        print(f"{result}\n")


def write() -> None:
    if check_disks() != "Данные невозможно востановить":
        global index_of_disk

        while True:
            index = int(input("\nВведите индекс строки для записи в диапазоне[0;63]: "))
            if  int(index) > 63 or int(index) < 0:
                print("введенный индекс вне диапазона [0;63].")
            else:
                break

        while True:
            input_data = str(input("Введите строку (10 байт): "))
            if len(input_data) != 10:
                print("Длина строки должна состоять из 10 байт.")
            else:
                break

        blocks = [input_data[:3], input_data[3:5], input_data[5:8], input_data[8:10]]
        for i in range(len(blocks)):
            while (len(blocks[i]) < 3):
                blocks[i] = ''.join(chr(0)) + blocks[i]

        # Обновляем данные для первой и второй группы
        excess_data1 = xor(blocks[0], blocks[1])
        excess_data2 = xor(blocks[2], blocks[3])

        index_of_disk.append(index)
        index_of_disk = list(set(index_of_disk))
        l1 = ['', '', '']
        l2 = ['', '', '']

        l1[index % 3] = excess_data1
        l2[index % 3] = excess_data2
        indexes = [x for x in range(len(l1)) if x != index % 3]

        l1[indexes[0]] = blocks[0]
        l1[indexes[1]] = blocks[1]

        l2[indexes[0]] = blocks[2]
        l2[indexes[1]] = blocks[3]

        result_data = []
        for x in disks:
            file = open(x, "r")
            result_data.append(file.readlines())
            file.close()

        for i in range(len(RAID_5_1)):
            result_data[i][index] = l1[i] + '\n'
            result_data[i+3][index] = l2[i] + '\n'

        for i in range(len(disks)):
            file = open(disks[i], "w")
            for j in range(len(result_data[0])):
                file.write(result_data[i][j])
            file.close()

        print('Данные записаны в строку под индексом {}.\n'.format(index))


def files() -> None:
    global disks
    for x in disks:
        if not os.path.exists(x):
            with open(x, "w") as file:
                for i in range(64):
                    file.write("_\n")
        else:
            with open(x, "r") as file:
                lines = file.readlines()
                if len(lines) == 0:
                    with open(x, "w") as file_append:
                        for i in range(64):
                            file_append.write("_\n")
                else:
                    with open(x, "w") as file:
                        for i in range(64):
                            file.write("_\n")


if __name__ == '__main__':
    files()
    file = open(RAID_5_1[0], 'r')
    data = file.readlines()
    for i in range(len(data)):
        if data[i] != "_\n":
            index_of_disk.append(i)
    file.close()
    while True:
        print("----- Меню действий -----")
        print("[1] - Записать данные.")
        print("[2] - Прочитать данные.")
        print("[0] - Выход.")
        print("-------------------------")

        x = input("Выберите действие: ")
        if x == '1':
            write()
        elif x == '2':
            read()
        elif x == '0':
            break
        else:
            print("Такой команды нет.")