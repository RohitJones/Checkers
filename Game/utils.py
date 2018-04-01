def generate_checker_board(size):
    return [
        [1 if x % 2 == 0 else 0 for x in range(size)]
        if y % 2 == 0
        else
        [0 if x % 2 == 0 else 1 for x in range(size)]

        for y in range(size)
    ]


def get_clicked_tile(search_x, search_y, rect_pos, size):
    for y_index in range(size):  # size of board
        for x_index in range(size):
            check_x, check_y = rect_pos[(x_index, y_index)]
            if check_y <= search_y <= check_y + 100 and check_x <= search_x <= check_x + 100:
                row, col = y_index, x_index
                return row, col

    return -1, -1
