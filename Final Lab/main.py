# Thupten Dukpa
# ES20BTECH11029
# CS2323 Lab 8


# This function converts a hexadecimal value to its binary equivalent
def to_binary(s):
    res = ""
    for hex_character in s:
        res = res + (hex_to_bin[hex_character])
    return res


# This function takes a sign-extended value and returns its decimal equivalent
def decimal_from_signextended(temp1):
    immed = 0
    if temp1[0] == '1':
        # takes care of 2's complement
        temp = temp1.replace('0', '2')
        temp = temp.replace('1', '0')
        temp = temp.replace('2', '1')
        immed = int(bin(int(temp, 2) + 1), 2)
        immed *= -1
    else:
        immed = int(temp1, 2)
    return immed


if __name__ == '__main__':
    file = open("input.txt", "r")
    output_file = open("output.txt", "w")

    lines = file.readlines()
    lines = [x.strip() for x in lines]

    hex_to_bin = {'0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100', '5': '0101', '6': '0110', '7': '0111',
                '8': '1000', '9': '1001', 'a': '1010', 'b': '1011', 'c': '1100', 'd': '1101', 'e': '1110', 'f': '1111'}

    format_type = {'0110011': 'r', '0010011': 'i', '0000011': 'il', '0100011': 's', '1100011': 'b',
                '1101111': 'jal', '1100111': 'jalr', '0110111': 'lui'}

    R = {'0000000000': 'add ', '0000100000': 'sub ', '1000000000': 'xor ', '1100000000': 'or ', '1110000000': 'and ',
        '0010000000': 'sll ', '1010000000': 'srl ', '1010100000': 'sra '}

    I = {'000': 'addi ', '100': 'xori ', '110': 'ori ', '111': 'andi ', '0010000000': 'slli ', '1010000000': 'srli ',
        '1010100000': 'srai '}

    L = {0: 'lb ', 1: 'lh ', 2: 'lw ', 3: 'ld ', 4: 'lbu ', 5: 'lhu ', 6: 'lwu '}

    S = {0: 'sb ', 1: 'sh ', 2: 'sw ', 3: 'sd '}

    B = {0: 'beq ', 1: 'bne ', 4: 'blt ', 5: 'bge ', 6: 'bltu ', 7: 'bgeu '}

    labels = list()  # contains list of labels, if 0, gets added to line.

    for line in lines:
        if line.startswith("0x"):
            line = line[2:]
        binary_line = to_binary(line)
        opcode = binary_line[-7:]

        if opcode not in format_type.keys() or len(line) < 8:
            error = f"Error in instruction {line}\n"
            print(error, end='')
            output_file.write(error)
            continue

        res = ""
        funct3 = binary_line[-15: -12]
        funct7 = binary_line[-32: -25]
        rs1 = int(binary_line[-20: -15], 2)
        rd = int(binary_line[-12: -7], 2)

        labels = [x-4 for x in labels]
        for i in range(len(labels)):
            if labels[i] == 0:
                res = f"L{i + 1}: "
                labels[i] = -1

        if format_type[opcode] == 'r':
            f = funct3 + funct7
            res = R[f]
            rs2 = int(binary_line[-25: -20], 2)
            res = res + f"x{rd}, x{rs1}, x{rs2}"

        if format_type[opcode] == 'i':
            temp1 = binary_line[-32: -20]

            if funct3 == '001' or funct3 == '101':
                f = funct3 + funct7
                immed = decimal_from_signextended(temp1[-5:])
            else:
                f = funct3
                immed = decimal_from_signextended(temp1)

            res = res + I[f] + f"x{rd}, x{rs1}, {immed}"

        if format_type[opcode] == 'il':
            hex_funct3 = int(funct3, 2)  # since funct3 in load instructions range only from 0 to 6

            temp1 = binary_line[-32: -20]

            immed = decimal_from_signextended(temp1)

            res = res + L[hex_funct3] + f"x{rd}, {immed}(x{rs1})"

        if format_type[opcode] == 's':
            hex_funct3 = int(funct3, 2)  # since funct3 in store instructions range only from 0 to 6
            temp = binary_line[-32: -25] + binary_line[-12: -7]
            immed = decimal_from_signextended(temp)
            rs2 = int(binary_line[-25: -20], 2)
            res = res + S[hex_funct3] + f"x{rs2}, {immed}(x{rs1})"

        if format_type[opcode] == 'b':
            hex_funct3 = int(funct3, 2)  # since funct3 in store instructions range only from 0, 1 and 4 to 7
            # last bit in b-type is always 0
            immed = decimal_from_signextended(binary_line[-8] + binary_line[-31: -26] + binary_line[-12: -8] + '0')
            rs2 = int(binary_line[-25: -20], 2)

            if immed not in labels:
                labels.append(immed)

            if immed < 0:
                val = immed
            else:
                val = f"L{labels.index(immed) + 1}"
            res = res + B[hex_funct3] + f"x{rs1}, x{rs2}, {val}"

        if format_type[opcode] == 'jal':
            immed = decimal_from_signextended(binary_line[-32] + binary_line[-20: -12] + binary_line[-20] + binary_line[-31: -20])

            if immed not in labels:
                labels.append(immed)
            res = res + f"jal x{rd}, L{labels.index(immed) + 1}"

        if format_type[opcode] == 'jalr':
            temp1 = binary_line[-32: -20]
            immed = int(temp1, 2)

            if immed not in labels:
                labels.append(immed)
            res = res + f"jalr x{rd}, x{rs1}, {immed}"

        if format_type[opcode] == 'lui':
            immed = hex(int(binary_line[-32: -12], 2))
            res = res + f"lui x{rd}, {immed}"

        output_file.write(res + "\n")
        print(res)

    output_file.close()
    file.close()

# End of code