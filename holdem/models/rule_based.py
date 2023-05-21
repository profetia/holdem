import numpy as np
from .agent import Agent


class RuleBasedAgent(Agent):
    def __init__(self, num_actions):
        self.num_actions = num_actions

    def step(self, state):
        #state space
        # Index	Meaning
        # 0~12	Spade A ~ Spade K
        # 13~25	Heart A ~ Heart K
        # 26~38	Diamond A ~ Diamond K
        # 39~51	Club A ~ Club K
        # 52~56	Raise number in round 1
        # 57~61	Raise number in round 2
        # 62~66	Raise number in round 3
        # 67~71	Raise number in round 4
        #action space
        # Action ID	Action
        # 0	Call
        # 1	Raise
        # 2	Fold
        # 3	Check
        cards = []
        for i in range(52):
            cards.append(i) if state["obs"][i] == 1 else None
        num_cards = len(cards)
        action = -1
        if num_cards == 2:
            #one pair, raise
            if cards[0] % 13 == cards[1] % 13:
                action = 1
            else:
                if 0 in state["legal_actions"]:
                    action = 0
                else:
                    action = 1
        if num_cards == 7:
            hand = Hand(cards)
            if hand.level == 1:
                action = 2
            elif hand.level <= 3:
                if 3 in state["legal_actions"]:
                    action = 3
                else:
                    action = 2
            elif hand.level <= 5:
                if 0 in state["legal_actions"]:
                    action = 0
                else:
                    action = 1
            elif hand.level <= 7:
                action = 1
            
        score = self.calculate_sum(cards)
        if num_cards == 5:
            if score < 4:
                action = 2
            elif score < 15:
                if 3 in state["legal_actions"]:
                    action = 3
                else:
                    action = 2
            elif score < 25:
                if 0 in state["legal_actions"]:
                    action = 0
                else:
                    action = 1
            else:
                action = 1
        elif num_cards == 6:
            if score < 3:
                action = 2
            elif score < 10:
                if 3 in state["legal_actions"]:
                    action = 3
                else:
                    action = 2
            elif score < 20:
                if 0 in state["legal_actions"]:
                    action = 0
                else:
                    action = 1
            else:
                action = 1
        if action == -1:
            action = np.random.choice(list(state["legal_actions"].keys()))
        return action

            


    def eval_step(self, state):
        probs = [0 for _ in range(self.num_actions)]
        for i in state["legal_actions"]:
            probs[i] = 1 / len(state["legal_actions"])

        info = {}
        info["probs"] = {
            state["raw_legal_actions"][i]: probs[
                list(state["legal_actions"].keys())[i]
            ]
            for i in range(len(state["legal_actions"]))
        }

        return self.step(state), info
    
    def calculate_sum(self,cards):
        weight = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
        #drow cards until 7 cards
        remain_cards = list(set([i for i in range(52)]) - set(cards))
        sum = 0
        for i in range(1000):
            while len(cards) < 7:
                cards.append(remain_cards.pop(np.random.randint(0, len(remain_cards))))
            hand = Hand(cards)
            sum += weight[hand.level]
        return sum / 1000




# alter the card id into color
def id2color(card):
    return card % 4

# alter the card id into number
def id2num(card):
    return card // 4

'''
hand.level
牌面等级：高牌 1  一对 2  两对 3  三条 4  顺子 5  同花 6  葫芦 7  四条 8  同花顺 9  皇家同花顺：10

'''
def judge_exist(x):
    if x >= 1:
        return True
    return False

# poker hand of 7 card
class Hand(object):
    def __init__(self, cards):
        cards = cards[:]
        self.level = 0
        self.cnt_num = [0] * 13
        self.cnt_color = [0] * 4
        self.cnt_num_eachcolor = [[0 for col in range(13)] for row in range(4)]
        self.maxnum = -1
        self.single = []
        self.pair = []
        self.tripple = []
        self.nums = []
        for x in cards:
            self.cnt_num[id2num(x)] += 1
            self.cnt_color[id2color(x)] += 1
            self.cnt_num_eachcolor[id2color(x)][id2num(x)] += 1
            self.nums.append(id2num(x))

        self.judge_num_eachcolor = [[] for i in range(4)]

        for i in range(4):
            self.judge_num_eachcolor[i] = list(map(judge_exist, self.cnt_num_eachcolor[i]))


        self.nums.sort(reverse=True)
        for i in range(12, -1, -1):
            if self.cnt_num[i] == 1:
                self.single.append(i)
            elif self.cnt_num[i] == 2:
                self.pair.append(i)
            elif self.cnt_num[i] == 3:
                self.tripple.append(i)
        self.single.sort(reverse=True)
        self.pair.sort(reverse=True)
        self.tripple.sort(reverse=True)

        # calculate the level of the poker hand
        for i in range(4):
            if self.judge_num_eachcolor[i][8:13].count(True) == 5:
                self.level = 10
                return


        for i in range(4):

            for j in range(7, -1, -1):
                if self.judge_num_eachcolor[i][j:j+5].count(True) == 5:
                    self.level = 9
                    self.maxnum = j + 4
                    return
            if self.judge_num_eachcolor[i][12] and self.judge_num_eachcolor[i][:4].count(True) == 4:
                    self.level = 9
                    self.maxnum = 3
                    return

        for i in range(12, -1, -1):
            if self.cnt_num[i] == 4:
                self.maxnum = i
                self.level = 8
                for j in range(4):
                    self.nums.remove(i)
                return

        tripple = self.cnt_num.count(3)
        if tripple > 1:
            self.level = 7
            return
        elif tripple > 0:
            if self.cnt_num.count(2) > 0:
                self.level = 7
                return

        for i in range(4):
            if self.cnt_color[i] >= 5:
                self.nums = []
                for card in cards:
                    if id2color(card) == i:
                        self.nums.append(id2num(card))
                self.nums.sort(reverse=True)
                self.nums = self.nums[:5]
                self.maxnum = self.nums[0]
                self.level = 6
                return

        for i in range(8, -1, -1):
            flag = 1
            for j in range(i, i + 5):
                if self.cnt_num[j] == 0:
                    flag = 0
                    break
            if flag == 1:
                self.maxnum = i + 4
                self.level = 5
                return
        if self.cnt_num[12] and list(map(judge_exist, self.cnt_num[:4])).count(True) == 4:
            self.maxnum = 3
            self.level = 5
            return

        for i in range(12, -1, -1):
            if self.cnt_num[i] == 3:
                self.maxnum = i
                self.level = 4
                self.nums.remove(i)
                self.nums.remove(i)
                self.nums.remove(i)
                self.nums = self.nums[:min(len(self.nums), 2)]
                return


        if self.cnt_num.count(2) > 1:
            self.level = 3
            return


        for i in range(12, -1, -1):
            if self.cnt_num[i] == 2:
                self.maxnum = i
                self.level = 2

                self.nums.remove(i)
                self.nums.remove(i)
                self.nums = self.nums[:min(len(self.nums), 3)]
                return


        if self.cnt_num.count(1) == 7:
            self.level = 1
            self.nums = self.nums[:min(len(self.nums), 5)]
            return

        self.level = -1

    def __str__(self):
        return 'level = %s' % self.level


def cmp(x,y):  # x < y return 1
    if x > y: return -1
    elif x == y: return 0
    else: return 1

# find the bigger of two poker hand(7 cards), if cards0 < cards1 then return 1, cards0 > cards1 return -1, else return 0
def judge_two(cards0, cards1):
    hand0 = Hand(cards0)
    hand1 = Hand(cards1)
    if hand0.level > hand1.level:
        return -1
    elif hand0.level < hand1.level:
        return 1
    else:
        if hand0.level in [5, 9]:
            return cmp(hand0.maxnum, hand1.maxnum)
        elif hand0.level in [1, 2, 4]:
            t = cmp(hand0.maxnum, hand1.maxnum)
            if t == 1: return 1
            elif t == -1: return -1
            else:
                if hand0.nums < hand1.nums:
                    return 1
                elif hand0.nums == hand1.nums:
                    return 0
                else:
                    return -1

        elif hand0.level == 6:
            if hand0.nums < hand1.nums:
                return 1
            elif hand0.nums > hand1.nums:
                return -1
            else:
                return 0

        elif hand0.level == 8:
            t = cmp(hand0.maxnum, hand1.maxnum)
            if t == 1:
                return 1
            elif t == -1:
                return -1
            else:
                return cmp(hand0.nums[0], hand1.nums[0])

        elif hand0.level == 3:
            if cmp(hand0.pair[0], hand1.pair[0]) != 0:
                return cmp(hand0.pair[0], hand1.pair[0])
            elif cmp(hand0.pair[1], hand1.pair[1]) != 0:
                return cmp(hand0.pair[1], hand1.pair[1])
            else:
                hand0.pair = hand0.pair[2:]
                hand1.pair = hand1.pair[2:]
                tmp0 = hand0.pair + hand0.pair + hand0.single
                tmp0.sort(reverse=True)
                tmp1 = hand1.pair + hand1.pair + hand1.single
                tmp1.sort(reverse=True)
                if tmp0[0] < tmp1[0]:
                    return 1
                elif tmp0[0] == tmp1[0]:
                    return 0
                else:
                    return -1

        elif hand0.level == 7:
            if cmp(hand0.tripple[0], hand1.tripple[0]) != 0:
                return cmp(hand0.tripple[0], hand1.tripple[0])
            else:
                tmp0 = hand0.pair
                tmp1 = hand1.pair
                if len(hand0.tripple) > 1:
                    tmp0.append(hand0.tripple[1])
                if len(hand1.tripple) > 1:
                    tmp1.append(hand1.tripple[1])
                tmp0.sort(reverse=True)
                tmp1.sort(reverse=True)
                if tmp0[0] < tmp1[0]:
                    return 1
                elif tmp0[0] == tmp1[0]:
                    return 0
                else:
                    return -1
        else:
            pass
            # assert 0
        return 0
