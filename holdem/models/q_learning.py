import numpy as np
from .agent import Agent


class QLearningAgent(Agent):
    def __init__(self, num_actions, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.num_actions = num_actions
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.step_count = 0
    
    def getQValue(self, state, action):
        state = tuple(state)
        if (state, action) not in self.q_table:
            self.q_table[(state, action)] = 0.0
        return self.q_table[(state, action)]
    
    def computeValueFromQValues(self, state):
        tmp = np.zeros(self.num_actions)
        for action in range(self.num_actions):
            tmp[action] = self.getQValue(state, action)
        return tmp.max()
    
    def computeActionFromQValues(self, state):
        tmp = np.zeros(self.num_actions)
        for action in range(self.num_actions):
            tmp[action] = self.getQValue(state, action)
        return tmp.argmax()

    def step(self, state):
        legalActions = state["legal_actions"]
        action = None
        if not legalActions:
            return None
        action = self.computeActionFromQValues(state["obs"]) if np.random.rand() > self.epsilon else np.random.choice(list(legalActions.keys()))
        return action
    
    def update(self, state, action, nextState, reward):
        legalActions = nextState["legal_actions"]
        state = state["obs"]
        nextState = nextState["obs"]
        if not legalActions:
            return None
        q_value = self.getQValue(state, action)
        next_max_q_value = self.computeValueFromQValues(nextState)
        update = reward + self.gamma * next_max_q_value - q_value
        self.q_table[(tuple(state), action)] += self.alpha * update


    def eval_step(self, state):
        self.step_count += 1
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
        action = self.step(state)
        if self.step_count % 100 == 0:
            self.save(r"D:\long\SHTU\2023Spring\CS181\project\holdem\experiments\qlearning\q_table.npy")
        return action, info
    
    def feed(self, ts):
        (state, action, reward, next_state, done) = tuple(ts)
        self.update(state, action, next_state, reward)

    def save(self, filename):
        np.save(filename, self.q_table)
    
    def load(self, filename):
        self.q_table = np.load(filename, allow_pickle=True).item()