import os
import json
import argparse
from typing import Any, Dict, List, Tuple
import torch

from holdem.utils import Logger, set_global_seed
from holdem.environment import Env, num_actions, state_shape

from benchmark.agents import create_agent

def create_game(config:Dict[str, Any]) -> Tuple[Env, List]:
    agents = [
        create_agent(agent_config["agent"], **agent_config["args"])
        for agent_config in config["agents"]
    ]
    num_players = len(agents)
    seed = config["settings"].get("seed", 3407)
    __env_config: Dict[str, Any] = {"num_players": num_players, "seed": seed}
    set_global_seed(seed=seed)
    env = Env(**__env_config, agents=agents)
    return env, agents

def run_game(args):

    print(f"Loading config from {args.config}")
    with open(args.config, "r") as f:
        config = json.load(f)
    
    env, agents = create_game(config=config)
    print(agents)

    total_rounds = config["settings"].get("total_rounds", 1000)

    for episode in range(total_rounds):
        trajectories, payoffs = env.run(is_training=True)
        print(trajectories)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        default="benchmark/config/game_random+dqn.json",
    )
    parser.add_argument(
        "--logdir",
        type=str,
        default="experiments",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="test",
    )

    args = parser.parse_args()
    run_game(args)