#challenges.thecatch.cz 8000
import socket, random, time
import sys, json, md5


#         +  -|   |-  T  _|_  L  _|   |- -|
blk = """X1X X1X X1X X0X X1X X10 01X X0X X0X
         111 110 011 111 111 011 110 011 110
         X1X X1X X1X X1X X0X X0X X0X X10 01X"""

class Game:
    BOARDSIZE = 15

    def __init__(self):
        self.board = None
        self.patterns = zip(*[[[int(q) if q.isdigit() else None for q in b] for b in a.strip().split(' ')] for a in blk.split('\n')])
        self.patsymbs = [sum([len([c for c in b if c == 1]) for b in a]) for a in self.patterns]

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
        sys.stdout.flush()            

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

        move = self.getnext(debug=False)

        if debug:
            print 'My move', move
            self.print_board2()
        return move


    def getnext(self,debug=False):

        def valid(i,j):
            if j>= 0 and j<Game.BOARDSIZE and i>=0 and i<Game.BOARDSIZE:
                return True
            return False


        def mark(i,j):
            for y in [-1,0,1]:
                for x in [-1,0,1]:
                    if valid(i+x,j+y) and self.board[j+y][i+x] == None:
                        self.board[j+y][i+x] = 8
                   
            return
            for j in [i-Game.BOARDSIZE - 1, i-Game.BOARDSIZE, i-Game.BOARDSIZE+1] + [i-1, i, i + 1] + [i+Game.BOARDSIZE - 1, i+Game.BOARDSIZE, i+Game.BOARDSIZE+1]:
                if not valid(j) or (self.board[j] != None): continue
                self.board[j] = 8


        def markNeigh(i,j, pat): #copy pattern to the board; mark neighbourghs
            for y,py in zip([-1,0,1],pat):
                for x,px in zip([-1,0,1],py):
                    if valid(i+x,j+y) and px in [1,3]: #self.board[j+y][i+x] == 1:
                       mark(i+x,j+y)
                       self.board[j+y][i+x] = 3

        def getNeigh(i, j):
            return [[self.board[j+y][i+x] if valid(i+x, j+y) else 0 for x in [-1,0,1]] for y in [-1,0,1]]
            

        def ishit(a, p, exactMatch=False,countOnesOnly=False):
            if (a == None) and (exactMatch): return False
            if (p == None) and (not exactMatch): return True
            if (a != None): a = a & 3
#            if a in [0, 8]: a=0
#            if a in [1, 5]: a=1
            if countOnesOnly and a==0: return False
            return a == p

        def ismiss(a, p):
            if (a == None): return False
            if (p == None): return False
            a = a & 3
#            if a in [0, 8]: a=0
#            if a in [1, 5]: a=1
            return a != p


        def getScore(m, pat, exactMatch=False, countOnesOnly=False):
            return sum([sum([1 if ishit(c,d,exactMatch,countOnesOnly) else -100 if ismiss(c,d) else 0 for c,d in zip(a,b)]) for a,b in zip(m,pat)])

        def pat2xy(i,j,pat):
            r = []
            for y,py in zip([-1,0,1],pat):
                for x,px in zip([-1,0,1],py):
                    if valid(i+x,j+y) and px == 1 and self.board[j+y][i+x] == None:
                       r.append((j+y)*Game.BOARDSIZE + i + x)
            if valid(i,j) and self.board[j][i] == None:
                r.append((j)*Game.BOARDSIZE + i)
            return r

        #try eliminate
        for i in range(0,Game.BOARDSIZE):
            for j in range(0,Game.BOARDSIZE):
                if self.board[j][i] in [0,3]: continue #3x3 block already done or miss
                n = getNeigh(i,j)
                hits = len([a for a in reduce(lambda x,y:x+y, n) if a==1]) #the nuber of hits

                for syms, pat in zip(self.patsymbs, self.patterns):
                    sc = getScore(n, pat)
                    if sc < 0: continue
                    if sc == 9:
                        #3x3 matched completely
                        markNeigh(i, j, pat)
                    elif hits == 3:
                        #three positive hits -> eliminate non-essential cells
                        sck = getScore(n, pat, exactMatch=True, countOnesOnly=True)
                        if (sck >= 3):
                            for x,y in [[-2,0],[0,-2],[0,2],[-2,0]]: #mark zeros near to 1 outside 3x3 block
                                if valid(i+x,j+y) and self.board[j+y][i+x] == None and self.board[j+y/2][i+x/2] in [3,1]:
                                    self.board[j+y][i+x] = 8
                            for y,py in zip([-1,0,1],pat): #mark zeros inside 3x3 block
                                for x,px in zip([-1,0,1],py):
                                    if valid(i+x,j+y) and px==None and self.board[j+y][i+x] == None:
                                        self.board[j+y][i+x] = 8

        #get scores
        scores = {}
        for i in range(0,Game.BOARDSIZE):
            for j in range(0,Game.BOARDSIZE):
                if self.board[j][i] in [0,3]: continue #already done or miss
                idx = j*Game.BOARDSIZE+i
                n = getNeigh(i,j)
                unk = len([a for a in reduce(lambda x,y:x+y, n) if a==None]) #the nuber of unknown

                for syms, pat in zip(self.patsymbs, self.patterns):
                    sc = getScore(n, pat, exactMatch=True, countOnesOnly=True)
                    if (sc < 0) or (sc == syms): continue

                    sc = sc*20 + syms

                    for p2 in pat2xy(i,j,pat):
                        if (not p2 in scores) or (scores[p2] < sc):
                           scores[p2] = sc

                    if (not unk): continue
                    #prioritize empty 3x3
                    sc += 10
                    if (not idx in scores) or (scores[idx] < sc):
                       scores[idx] = sc

        #keep only empty cells
        scores = dict([(k, scores[k]) for k in scores if self.board[k//Game.BOARDSIZE][k%Game.BOARDSIZE]==None])
        if len(scores) == 0: #we already won, we don't need to guess; take a random cell
            for i in range(0,Game.BOARDSIZE):
                for j in range(0,Game.BOARDSIZE):
                    if self.board[j][i] in [3,8,None]:
                        scores[j*Game.BOARDSIZE + i] = 1
            
        maxscore = max(scores.values())
        cells = [k for k in scores if scores[k] == maxscore]
        xy = random.choice(cells)
        y,x = xy // Game.BOARDSIZE, xy % Game.BOARDSIZE
        self.board[y][x] = 2

        if debug:
            print 'max score', maxscore
            for j in range(0,Game.BOARDSIZE):
                for i in range(0,Game.BOARDSIZE):
                    idx = j*Game.BOARDSIZE+i
                    s = scores[idx] if idx in scores else 0
                    print "%s[%4.1f]" % ({None:'?',1:'X',0:' ',2:'p',8:'0',3:'1'}[self.board[j][i]],s),
                print

        return chr(ord('A') + y) + str(x+1)


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
