import os

disks = ['disk_0.txt', 'disk_1.txt', 'disk_2.txt', 'disk_3.txt', 'disk_4.txt', 'disk_5.txt']

RAID_5_1 = ['disk_0.txt', 'disk_1.txt', 'disk_2.txt']
RAID_5_2 = ['disk_3.txt', 'disk_4.txt', 'disk_5.txt']
disks_indexes = []



def xor_two_str(a: str, b: str) -> str:
    return ''.join([chr(ord(x) ^ ord(y)) for x, y in zip(a, b)])

def reconstruction(disks_index: int) -> None:
    global disks_indexes
    global RAID_5_1
    global RAID_5_2

    if disks_index < 3:
        problematische_Raid = RAID_5_1
        problematische_index = disks_index
    else:
        problematische_Raid = RAID_5_2
        problematische_index = disks_index - 3

    lost_data = []
    list_of_data = []
    for i in range(len(problematische_Raid)):
        if i != problematische_index:
            file = open(problematische_Raid[i], 'r')
            list_of_data += [[x for x in file.readlines() if x != '_\n']]
            file.close()
        else:
            list_of_data += [["*" * 4] * 64]

    for i in range(len(list_of_data[0])):
        small_list_of_data = []
        for j in range(len(list_of_data)):
            small_list_of_data.append(list_of_data[j][i].strip())

        indexes = [x for x in range(len(small_list_of_data)) if small_list_of_data[x] != '*' * 4]

        lost_data.append(xor_two_str(small_list_of_data[indexes[0]], small_list_of_data[indexes[1]]).zfill(4))

    ind = 0
    with open(disks[disks_index], 'w') as file:
        for i in range(64):
            if i in disks_indexes:
                file.write(lost_data[ind] + '\n')
                ind += 1
            else:
                file.write("_\n")

    print("Диск {} был восстановлен.".format(disks_index))

def check_disks() -> None:
    for i in range(len(disks)):
        if not os.path.isfile(disks[i]):
            print("Диск {} был пуст.".format(i))
            reconstruction(i)
            break

def read() -> None:
    global disks_indexes
    if len(disks_indexes) == 0:
        print('Диски пусты.')
        return

    check_disks()
    while True:
        input_data = input("Введите индекс строки которую хотите прочитать [0;63] или введите \"b\" / \"back\" для возврата: ")
        if input_data == 'b' or input_data == 'back':
            return
        elif int(input_data) > 63:
            print("индекс вне диапазона [0;63].")
        elif int(input_data) not in disks_indexes:
            print("Данные не доступны для данного адреса.")
        else:
            break

    list_of_data = []

    for i in range(len(disks)):
        file = open(disks[i], 'r')
        list_of_data += [file.readlines()]
        file.close()

    result = ''
    input_data = int(input_data)
    for i in range(len(list_of_data)):
        if int(input_data % 3) != int(i % 3):
            if len(list_of_data[i][int(input_data)][:-1]) == 3:
                buf = str(list_of_data[i][int(input_data)][:-1])

                # while ''.join(chr(0)) in buf:
                #     buf = str
                if ''.join(chr(0)) in buf:
                    buf = buf.replace(''.join(chr(0)), '')
                result += buf
            else:
                if i < len(list_of_data)//2:
                    indexes = [ind for ind in range(len(list_of_data)//2) if ind != int(input_data % 3) and ind != i]
                    recover_string = list_of_data[int(input_data % 3)][input_data]
                else:
                    indexes = [ind for ind in range(len(list_of_data)//2, len(list_of_data)) if ind != int(input_data % 3) + 3 and ind != i]
                    recover_string = list_of_data[int(input_data % 3) + 3][input_data]
                result += xor_two_str(list_of_data[indexes[0]], recover_string)

    print("Данные по адресу {}:".format(input_data))
    print(result)

def write() -> None:
    check_disks()
    global disks_indexes

    while True:
        input_index = int(input("Введите индекс для записи [0;63]: "))
        if input_index > 63:
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
    excess_data1 = xor_two_str(blocks[0], blocks[1])
    excess_data2 = xor_two_str(blocks[0], blocks[2])

    disks_indexes.append(input_index)
    disks_indexes = list(set(disks_indexes))
    l1 = ['', '', '']
    l2 = ['', '', '']

    l1[input_index % 3] = excess_data1
    l2[input_index % 3] = excess_data2
    indexes = [x for x in range(len(l1)) if x != input_index % 3]

    l1[indexes[0]] = blocks[0]
    l2[indexes[0]] = blocks[1]

    l1[indexes[1]] = blocks[2]
    l2[indexes[1]] = blocks[3]

    data_for_write = []
    for x in disks:
        file = open(x, "r")
        data_for_write.append(file.readlines())
        file.close()

    for i in range(len(RAID_5_1)):
        data_for_write[i][input_index] = l1[i] + '\n'
        data_for_write[i+3][input_index] = l2[i] + '\n'

    for i in range(len(disks)):
        file = open(disks[i], "w")
        for j in range(len(data_for_write[0])):
            file.write(data_for_write[i][j])
        file.close()

    print('Данные записаны под индексом {}.'.format(input_index))

def fillng() -> None:
    global disks_indexes
    for x in disks:
        file = open(x, "r")
        if len(file.readlines()) == 0:
            file.close()
            file = open(x, "a")
            for i in range(64):
                file.write("_" + '\n')
            file.close()
        else:
            return

if __name__ == '__main__':
    fillng()
    file = open(RAID_5_1[0], 'r')
    data = file.readlines()
    for i in range(len(data)):
        if data[i] != "_\n":
            disks_indexes.append(i)
    file.close()
    while True:
        print("Записать данные - 1.")
        print("Прочитать данные - 2.")
        print("Выход - 0.")

        x = input("Выберите действие: ")
        if x == '1':
            write()
        elif x == '2':
            read()
        elif x == '0':
            break
        else:
            print("Такой команды нет.")