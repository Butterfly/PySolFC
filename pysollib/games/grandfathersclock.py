## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##

__all__ = []

# imports
import sys

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

# /***********************************************************************
# //
# ************************************************************************/

class GrandfathersClock_Hint(CautiousDefaultHint):
    # FIXME: demo is not too clever in this game

    def _getDropCardScore(self, score, color, r, t, ncards):
        # drop all cards immediately
        return 92000, color


# /***********************************************************************
# // Grandfather's Clock
# ************************************************************************/

class GrandfathersClock(Game):
    Hint_Class = GrandfathersClock_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 9 cards are fully playable in default window size)
        dh = max(3*l.YS/2+l.CH, l.YS+(9-1)*l.YOFFSET)
        self.setSize(10*l.XS+l.XM, l.YM+2*dh)

        # create stacks
        for i in range(2):
            x, y = l.XM, l.YM + i*dh
            for j in range(4):
                s.rows.append(RK_RowStack(x, y, self, max_move=1, max_accept=1))
                x = x + l.XS
        y = l.YM + dh - l.CH / 2
        self.setRegion(s.rows[:4], (-999, -999, x - l.XM / 2, y))
        self.setRegion(s.rows[4:], (-999,    y, x - l.XM / 2, 999999))
        d = [ (0,0), (1,0.15), (2,0.5), (2.5,1.5), (2,2.5), (1,2.85) ]
        for i in range(len(d)):
            d.append( (0 - d[i][0], 3 - d[i][1]) )
        x0, y0 = l.XM, l.YM + dh - l.CH
        for i in range(12):
            j = (i + 5) % 12
            x = int(round(x0 + ( 6.5+d[j][0]) * l.XS))
            y = int(round(y0 + (-1.5+d[j][1]) * l.YS))
            suit = (1, 2, 0, 3) [i % 4]
            s.foundations.append(SS_FoundationStack(x, y, self, suit,
                                                    base_rank=i+1, mod=13,
                                                    max_move=0))
        s.talon = InitialDealTalonStack(self.width-l.XS, self.height-l.YS, self)

        # define stack-groups
        self.sg.openstacks = s.foundations + s.rows
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    #
    # game overrides
    #
    def _shuffleHook(self, cards):
        # move clock cards to bottom of the Talon (i.e. last cards to be dealt)
        C, S, H, D = 0*13, 1*13, 2*13, 3*13
        ids = (1+S, 2+H, 3+C, 4+D, 5+S, 6+H, 7+C, 8+D, 9+S, 10+H, 11+C, 12+D)
        clocks = []
        for c in cards[:]:
            if c.id in ids:
                clocks.append(c)
                cards.remove(c)
        # sort clocks reverse by rank
        clocks.sort(lambda a, b: cmp(b.rank, a.rank))
        return clocks + cards

    def startGame(self):
        self.playSample("grandfathersclock", loop=1)
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)

    shallHighlightMatch = Game._shallHighlightMatch_RK

    def getHighlightPilesStacks(self):
        return ()

    def getAutoStacks(self, event=None):
        # disable auto drop - this would ruin the whole gameplay
        return ((), (), ())


# /***********************************************************************
# // Dial
# ************************************************************************/

class Dial(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+4*l.YS)

        x0, y0 = l.XM+2*l.XS, l.YM
        rank = 0
        for xx, yy in ((3.5, 0.15),
                       (4.5, 0.5),
                       (5,   1.5),
                       (4.5, 2.5),
                       (3.5, 2.85),
                       (2.5, 3),
                       (1.5, 2.85),
                       (0.5, 2.5),
                       (0,   1.5),
                       (0.5, 0.5),
                       (1.5, 0.15),
                       (2.5, 0),
                       (2.5, 1.5),
                       ):
            x = int(x0 + xx*l.XS)
            y = int(y0 + yy*l.YS)
            s.foundations.append(AC_FoundationStack(x, y, self, suit=ANY_SUIT,
                                 dir=0, max_cards=4, base_rank=rank, max_move=0))
            rank += 1

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=2)
        l.createText(s.talon, 's')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')

        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Hemispheres
# ************************************************************************/

BLACK, RED = 0, 1


class Hemispheres_Hint(DefaultHint):
    def shallMovePile(self, from_stack, to_stack, pile, rpile):
        if not self._defaultShallMovePile(from_stack, to_stack, pile, rpile):
            return False
        if from_stack in self.game.s.rows and to_stack in self.game.s.rows:
            # check for loops
            return len(from_stack.cards) == 1
        return True


class Hemispheres_RowStack(SC_RowStack):

    def _canSwapPair(self, from_stack):
        if from_stack not in self.game.s.rows[4:]:
            return False
        if len(self.cards) != 1 or len(from_stack.cards) != 1:
            return False
        if self in self.game.s.rows[4:10]:
            alt_rows = self.game.s.rows[10:]
            color = RED
        else:
            alt_rows = self.game.s.rows[4:10]
            color = BLACK
        if from_stack not in alt_rows:
            return False
        c0, c1 = from_stack.cards[0], self.cards[0]
        return c0.color == color and c1.color != color

    def acceptsCards(self, from_stack, cards):
        if self._canSwapPair(from_stack):
            return True
        if not SC_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if self in self.game.s.rows[4:10]:
            if cards[0].color == BLACK:
                return False
            return (from_stack in self.game.s.rows[4:10] or
                    from_stack is self.game.s.waste)
        if self in self.game.s.rows[10:]:
            if cards[0].color == RED:
                return False
            return (from_stack in self.game.s.rows[10:] or
                    from_stack is self.game.s.waste)
        return False

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if self._canSwapPair(to_stack):
            self._swapPairMove(ncards, to_stack, frames=-1, shadow=0)
        else:
            SC_RowStack.moveMove(self, ncards, to_stack,
                                 frames=frames, shadow=shadow)

    def _swapPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        swap = game.s.internals[0]
        game.moveMove(n, self, swap, frames=0)
        game.moveMove(n, other_stack, self, frames=frames, shadow=shadow)
        game.moveMove(n, swap, other_stack, frames=0)
        game.leaveState(old_state)


class Hemispheres(Game):
    Hint_Class = Hemispheres_Hint

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+9.5*l.XS, l.YM+5*l.YS)

        # internal stack (for swap)
        s.internals.append(InvisibleStack(self))

        x0, y0 = l.XM+1.5*l.XS, l.YM
        # barriers
        for xx, yy in ((0,   2),
                       (7,   2),
                       (3.5, 0),
                       (3.5, 4),
                       ):
            x, y = x0+xx*l.XS, y0+yy*l.YS
            s.rows.append(BasicRowStack(x, y, self, max_accept=0))

        # northern hemisphere (red)
        for xx, yy in ((0.5, 1),
                       (1.5, 0.5),
                       (2.5, 0.3),
                       (4.5, 0.3),
                       (5.5, 0.5),
                       (6.5, 1),
                       ):
            x, y = x0+xx*l.XS, y0+yy*l.YS
            stack = Hemispheres_RowStack(x, y, self,
                                         base_color=RED, max_move=1)
            stack.CARD_YOFFSET = 0
            s.rows.append(stack)

        # southern hemisphere (black)
        for xx, yy in ((6.5, 3),
                       (5.5, 3.5),
                       (4.5, 3.8),
                       (2.5, 3.8),
                       (1.5, 3.5),
                       (0.5, 3),
                       ):
            x, y = x0+xx*l.XS, y0+yy*l.YS
            stack = Hemispheres_RowStack(x, y, self,
                                         base_color=BLACK, max_move=1, dir=1)
            stack.CARD_YOFFSET = 0
            s.rows.append(stack)

        # foundations
        x, y = x0+2*l.XS, y0+1.5*l.YS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=2+i/2,
                                                    max_move=0))
            x += l.XS
        x, y = x0+2*l.XS, y+l.YS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2,
                                 max_move=0, base_rank=KING, dir=-1))
            x += l.XS

        # talon & waste
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'ne')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'ne')

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        founds_cards = []               # foundations
        rows_cards = []                 # rows
        for c in cards[:]:
            if c.rank in (ACE, KING):
                if ((c.rank == ACE and c.color == RED) or
                    (c.rank == KING and c.color == BLACK)):
                    cards.remove(c)
                    founds_cards.append(c)
                elif c.deck == 0:
                    cards.remove(c)
                    rows_cards.append(c)
        founds_cards.sort(lambda a, b: cmp((-a.rank, -a.suit), (-b.rank, -b.suit)))
        rows_cards.sort(lambda a, b: cmp((a.rank, a.suit), (b.rank, b.suit)))
        return cards+rows_cards+founds_cards


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()       # deal first card to WasteStack


    def fillStack(self, stack):
        if stack in self.s.rows[4:] and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)


    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        # by color
        return card1.color == card2.color and abs(card1.rank-card2.rank) == 1



# register the game
registerGame(GameInfo(261, GrandfathersClock, "Grandfather's Clock",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(682, Dial, "Dial",
                      GI.GT_1DECK_TYPE, 1, 1, GI.SL_LUCK))
registerGame(GameInfo(690, Hemispheres, "Hemispheres",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED,
                      altnames=("The Four Continents",) ))

