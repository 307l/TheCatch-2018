#challenges.thecatch.cz 8000
import socket, random, time
import sys, json, md5


class Game:
    BOARDSIZE = 15

    def __init__(self):
        self.board = None

    def board2_hash(self):
        rr = ''
        for row in self.board:
            for col in row:
                rr += {None:' ',0:' ',1:'X', 2:'X', 8:' ', 3:'X'}[col]

        rr2 = ''
        for row in self.myboard:
            rr2 += ''.join([{'.':' ', 'o':' ','O':'X','X':'X'}[a] for a in row])

        return md5.new(rr).hexdigest(), md5.new(rr2).hexdigest()

    def print_board2(self):
        for row, rowmy in zip(self.board, self.myboard):
            rr = ''
            for col in row:
                rr += {None:'?',0:' ',1:'X',2:'*', 8:'0', 3:'1'}[col]

            rr += '   ' + rowmy

            rr += '  |  '
            for col in row:
                rr += {None:'.',0:' ',1:'X', 2:'*', 8:' ', 3:'X'}[col]

            rr += '   ' + ''.join([{'.':'.', 'o':' ','O':'X','X':'X'}[a] for a in rowmy])

            print rr
        print

    def p2xy(self, text):
        assert len(text)>1
        row = ord(text[0])-ord('A')
        assert row >= 0 and row < Game.BOARDSIZE
        col = int(text[1:])-1
        assert col >= 0 and col < Game.BOARDSIZE
   
        return (col,row)

    def procdata(self, data, debug=False):

        self.myboard = [data['board'][k] for k in sorted(data['board'].keys()) if k!='_']
        assert len(self.myboard) == Game.BOARDSIZE and len(self.myboard[0]) == Game.BOARDSIZE 

        end = (data['yourMoveResult'] == "You win this game") or (data["myMoveResult"] == "You lost this game")

        if (data['yourMove'] == '') and (data["myMove"] == ''):
            print("New game")
            self.board = [[None]*Game.BOARDSIZE for i in range(Game.BOARDSIZE)]
            self.srvmoves = []
        else:
            if data['myMove']:
                self.srvmoves.append(data['myMove'])

            if data['yourMove']:
                x,y = self.p2xy(data['yourMove'])
                self.board[y][x] = {'Missed':0,'Hit':1,'You win this game':1}[data['yourMoveResult']]

            if end:
                #no reply expected
                return None

#            print 'HASHES',self.board2_hash()
#            print 'MOVES',''.join(self.oponent)

        move = self.getnext()

        if debug:
            print 'My move', move
            self.print_board2()
        return move

    def getnext(self):

        p = []
        for i in range(0,Game.BOARDSIZE):
            for j in range(0,Game.BOARDSIZE):
                if self.board[j][i] == None:
                    p.append((i,j))


        i,j = random.choice(p)
        return chr(ord('A') + j) + str(i+1)


sock = socket.create_connection(('challenges.thecatch.cz', 8000))
try:
    g = Game()
    buf = ''
    while 1:
        data = sock.recv(4096)
        if not data: 
            break
        buf += data
        lt = time.time()

        while '\n{' in buf and '\n}' in buf:
            i = buf.index('\n{')
            j = buf.index('\n}',i)
            if i:
                print(buf[:i])
                sys.stdout.flush()
            data = json.loads(buf[i+1:j+2])
            buf = buf[j+2:]

            move = g.procdata(data,debug=True)
            if move == None:
                print('Score: %s' % data['overallResult'])
                continue

            sock.send(move+'\n') 
    print buf            
finally:
    print >>sys.stderr, 'closing socket'
    sock.close()
