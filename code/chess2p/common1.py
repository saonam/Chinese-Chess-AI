import numpy as np
import random
# from socketIO_client import SocketIO
import time
from piece_selector1 import *
from move_selector1 import *
from check import *
import copy as cp
import ctypes
import check as ck
# evaluator = ctypes.CDLL('/root/code/example.so')
evaluator = ctypes.CDLL('/data/ssd/public/zxm/code/example.so')

# from evaluate import *

piece_b = ['k', 'a', 'b', 'n', 'r', 'c', 'p']
piece_r = ['K', 'A', 'B', 'N', 'R', 'C', 'P']
piece_list = {'b': piece_b, 'r': piece_r}
piece_list_op = {'b': piece_r, 'r': piece_b}


precision = 18
move = np.zeros((precision, 4), dtype=np.int)

# load NN models
init_v = "001"
fuck1 = Fuck1()
fuck1.init_piece_selector_with_version(init_v)
fuck1_a = Fuck1_m("a")
fuck1_a.init_move_selector_with_version(init_v)
fuck1_b = Fuck1_m("b")
fuck1_b.init_move_selector_with_version(init_v)
fuck1_c = Fuck1_m("c")
fuck1_c.init_move_selector_with_version(init_v)
fuck1_k = Fuck1_m("k")
fuck1_k.init_move_selector_with_version(init_v)
fuck1_p = Fuck1_m("p")
fuck1_p.init_move_selector_with_version(init_v)
fuck1_r = Fuck1_m("r")
fuck1_r.init_move_selector_with_version(init_v)
fuck1_n = Fuck1_m("n")
fuck1_n.init_move_selector_with_version(init_v)


# get max value index from prediction
def get_max(prediction):
    temp = np.amax(prediction)
    for i in range(10):
        for j in range(9):
            if (temp == prediction[i][j]):
                return i, j

# process piece selector prediction
def process_piece(prediction, fen, player):
    for i in range(10):
        for j in range(9):
            temp_r, temp_c = flip(fen, i, j)    
            if (fen[i*10+j] == '1'):
                prediction[temp_r][temp_c]=0.0
            elif (fen[i*10+j] in piece_list_op[player]):
                prediction[temp_r][temp_c]=0.0

    prediction[prediction<0.01] = 0.0
    total = np.sum(prediction)
    prediction = prediction / total

    
# process move selector prediction
def process_move(prediction):
    prediction[prediction<0.01] = 0.0
    total = np.sum(prediction)
    prediction = prediction / total


def random_select(prediction):
    prediction[prediction<0.01] = 0.0
    total = np.sum(prediction)
    prediction = prediction / total

    rand = np.random.uniform(0,1)
    temp = 0
    for i in range(10):
        for j in range(9):
            temp += prediction[i][j]
            if (temp > rand):
                return i,j


def printstat(prediction):
    temp = np.zeros((10,9))
    np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
    for i in range(10):
        for j in range(9):
            temp[i][j] = prediction[9-i][8-j]
            print temp[i]


def flip(fen, x, y):
    if fen[100] =='b':
        x = 9 - x
        y = 8 - y
    return x, y


def move_selection(fen, newboard, randomness):

    prediction = fuck1.piece_selector_nn(fen)
    process_piece(prediction, fen, fen[100])
    # print prediction
    rand = random.uniform(0,1)
    if (rand < randomness):
        i = 0
        while (i < precision):

            move[i][0], move[i][1] = get_max(prediction)
            if prediction[move[i][0]][move[i][1]] == 0:
                break
            temp0 = move[i][0]
            temp1 = move[i][1]
            move[i][0], move[i][1] = flip(fen, move[i][0], move[i][1])

            # move selector
            output, piece_type = extract_features_dest(fen, [move[i][0], move[i][1]])
            if piece_type == "a":
                prediction_m = fuck1_a.move_selector_nn(output)
            elif piece_type == "b":
                prediction_m = fuck1_b.move_selector_nn(output)
            elif piece_type == "c":
                prediction_m = fuck1_c.move_selector_nn(output)
            elif piece_type == "n":
                prediction_m = fuck1_n.move_selector_nn(output)
            elif piece_type == "k":
                prediction_m = fuck1_k.move_selector_nn(output)
            elif piece_type == "p":
                prediction_m = fuck1_p.move_selector_nn(output)
            elif piece_type == "r":
                prediction_m = fuck1_r.move_selector_nn(output)
            pass

            # print prediction_m
            process_move(prediction_m)
            for j in range(4):
                if (i+j+1 >= precision):
                    break

                move[i+j][0] = move[i][0]
                move[i+j][1] = move[i][1]
                # process prediction
                move[i+j][2], move[i+j][3] = get_max(prediction_m)
                # print prediction_m[move[i+j][2]][move[i+j][3]]
                if prediction_m[move[i+j][2]][move[i+j][3]] == 0:
                    j -= 1
                    break
                temp2 = move[i+j][2]
                temp3 = move[i+j][3]
                move[i+j][2], move[i+j][3] = flip(fen, move[i+j][2], move[i+j][3])

                prediction_m[temp2][temp3] = 0.0

            i = i + j
            i = i + 1
            # print "i = %d" % i
            prediction[temp0][temp1] = 0.0
        # print "i = %d" % i
        index = eval_move(newboard, move[:i], i, fen[100])

    else:
        probs = np.zeros((4), dtype=np.float32)
        i = 0
        while (i < 4):

            move[i][0], move[i][1] = get_max(prediction)
            probs[i] = prediction[move[i][0]][move[i][1]]
            temp0 = move[i][0]
            temp1 = move[i][1]
            move[i][0], move[i][1] = flip(fen, move[i][0], move[i][1])

            # move selector
            output, piece_type = extract_features_dest(fen, [move[i][0], move[i][1]])
            if piece_type == "a":
                prediction_m = fuck1_a.move_selector_nn(output)
            elif piece_type == "b":
                prediction_m = fuck1_b.move_selector_nn(output)
            elif piece_type == "c":
                prediction_m = fuck1_c.move_selector_nn(output)
            elif piece_type == "n":
                prediction_m = fuck1_n.move_selector_nn(output)
            elif piece_type == "k":
                prediction_m = fuck1_k.move_selector_nn(output)
            elif piece_type == "p":
                prediction_m = fuck1_p.move_selector_nn(output)
            elif piece_type == "r":
                prediction_m = fuck1_r.move_selector_nn(output)
            pass

            # print prediction_m
            process_move(prediction_m)
            move[i][2], move[i][3] = get_max(prediction_m)
            probs[i] = probs[i] * prediction_m[move[i][2]][move[i][3]]
            move[i][2], move[i][3] = flip(fen, move[i][2], move[i][3])

            prediction[temp0][temp1] = 0.0
            i = i + 1
        index = probs.argmax()

    return index

def eval_move(board, move, size, side):
    score = np.zeros(size)
    depth = 1
    # print "oppo move"
    # print move
    for x in xrange(0,size):
        # execute the move
        newboard = cp.deepcopy(board)
        string = move[x]

        if(validate(board, move[x], side)==0):
            if (depth%2 == 0):
                score[x] = 99999
            else:
                score[x] = -99999
            continue

        newboard[int(string[2])][int(string[3])]=newboard[int(string[0])][int(string[1])]
        newboard[int(string[0])][int(string[1])]='1';

        fen = ""
        for i in xrange(0,10):
            for j in xrange(0,9):
                fen += newboard[i][j]
            fen += "/"
        # fen += side
        if side == 'r':
            fen += "b"
        else:
            fen += 'r'
            pass

        # print fen
        isChecked, _ = ck.check(newboard, side)
        if isChecked == 1:
            if (depth%2 == 0):
                score[x] = 10001
            else:
                score[x] = -10001
            continue
        # evaluator.evaluate.argtypes = [ctypes.c_char_p]
        # score[x]=evaluator.evaluate(fen)
        score[x] = eval_minimax(fen, fen[100], depth)
        # score[x] = evaluator_nn.evaluate(fen)
        # score[x] = evaluate(fen)
    if (depth%2 == 0):
        index = np.argmin(score)
    else:
        index = np.argmax(score)
    # print score
    # print index
    return index


def eval_minimax(fen, side, depth):
    newboard = [[0 for x in range(9)] for y in range(10)]
    for i in xrange(0,10):
        for j in xrange(0,9):
            newboard[i][j] = fen[i*10 + j]

    move = np.zeros((precision, 4), dtype=np.int)
    # score = move_selection_temp(fen, newboard, temp_move, depth)
    # return score
    # def move_selection_temp(fen, newboard, move, depth):

    prediction = fuck1.piece_selector_nn(fen)
    process_piece(prediction, fen, fen[100])

    i = 0
    while( i < precision):
        
        move[i][0], move[i][1] = get_max(prediction)
        if prediction[move[i][0]][move[i][1]] == 0:
            break
        temp0 = move[i][0]
        temp1 = move[i][1]
        move[i][0], move[i][1] = flip(fen, move[i][0], move[i][1])

        # move selector
        output, piece_type = extract_features_dest(fen, [move[i][0], move[i][1]])
        if piece_type == "a":
            prediction_m = fuck1_a.move_selector_nn(output)
        elif piece_type == "b":
            prediction_m = fuck1_b.move_selector_nn(output)
        elif piece_type == "c":
            prediction_m = fuck1_c.move_selector_nn(output)
        elif piece_type == "n":
            prediction_m = fuck1_n.move_selector_nn(output)
        elif piece_type == "k":
            prediction_m = fuck1_k.move_selector_nn(output)
        elif piece_type == "p":
            prediction_m = fuck1_p.move_selector_nn(output)
        elif piece_type == "r":
            prediction_m = fuck1_r.move_selector_nn(output)
        pass

        process_move(prediction_m)
        # process prediction
        for j in range(4):
            if (i+j+1 >= precision):
                break
            move[i+j][0] = move[i][0]
            move[i+j][1] = move[i][1]
            # process prediction
            move[i+j][2], move[i+j][3] = get_max(prediction_m)
            if prediction_m[move[i+j][2]][move[i+j][3]] == 0:
                break
            temp2 = move[i+j][2]
            temp3 = move[i+j][3]
            move[i+j][2], move[i+j][3] = flip(fen, move[i+j][2], move[i+j][3])

            prediction_m[temp2][temp3] = 0.0

        i = i + j
        i = i + 1

        prediction[temp0][temp1] = 0.0

    # index = eval_move(newboard,move[:i],i,fen[100])

    move = move[:i]
    size = i
    side = fen[100]
    score = np.zeros(size)
    # print "prediction move"
    # print move
    for x in xrange(0,size):
        tempboard = cp.deepcopy(newboard)
        string = move[x]
        tempboard[int(string[2])][int(string[3])]=tempboard[int(string[0])][int(string[1])]
        tempboard[int(string[0])][int(string[1])]='1';

        if(validate(newboard, move[x], side) == 0):
            if (depth%2 == 0):
                score[x] = -99999
            else:
                score[x] = 99999
            continue

        fen=""
        for i in xrange(0,10):
            for j in xrange(0,9):
                fen += tempboard[i][j]
            fen += "/"
        # fen += side
        if side=='r':
            fen += "b"
        else:
            fen += 'r'
            pass

        # print fen
        isChecked, _ = ck.check(tempboard, side)
        if (isChecked == 1):
            if (depth%2 == 0):
                score[x] = -10001
            else:
                score[x] = 10001
            continue
        if (depth == 1): 
            evaluator.evaluate.argtypes = [ctypes.c_char_p]
            score[x] = evaluator.evaluate(fen)
            # score[x] = evaluator_nn.evaluate(fen)
        else:
            score[x] = eval_minimax(fen, fen[100], depth-1)
    # print score
    # print "score is %d" % np.amin(score)
    if (depth%2 == 0):
        return np.amax(score)
    else:
        return np.amin(score)