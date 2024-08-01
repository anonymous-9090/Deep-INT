import argparse
from datetime import datetime
import os
import gymnasium as gym
from gymnasium.spaces import Box
import torch
import torch.nn as nn

from tianshou.data import Collector, VectorReplayBuffer
from tianshou.env import DummyVectorEnv
from tianshou.policy import PPOPolicy
from tianshou.trainer import OnpolicyTrainer
from tianshou.utils.net.common import ActorCritic, Net
from tianshou.utils.net.discrete import Actor, Critic
from torch.utils.tensorboard import SummaryWriter
from tianshou.utils import TensorboardLogger

from env.network_env import make_telemetry_env
from telemetry_pg.gcnac import GCNCategoricalActor, GCNCritic, GCN
from env.path_collector import path_Collector
from telemetry_pg.telemetry_policy_pg import TelemetryPG
from env.telemetry_onpolicytrainer import TelemetryTrainer
from env.path_collector import path_Collector

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--batch-size', type=int, default=512)
    parser.add_argument('-e', '--epoch', type=int, default=200)
    parser.add_argument('--step-per-epoch', type=int, default=1000)
    parser.add_argument('--repeat-per-collect', type=int, default=8)
    parser.add_argument('--episode-per-test', type=int, default=10)
    parser.add_argument('--step-per-collect', type=int, default=None)
    parser.add_argument('--episode-per-collect', type=int, default=50)
    
    parser.add_argument('--lr', type=float, default=0.00001)
    parser.add_argument('--wd', type=float, default=1e-4)
    parser.add_argument('--eps-clip', type=float, default=0.15)
    parser.add_argument('--lr-decay', type=bool, default=False)
    parser.add_argument('--lr-maxt', type=int, default=400)
    
    parser.add_argument('--buffer-size', type=int, default=5000)
    parser.add_argument('--seed', type=int, default=321)
    
    args = parser.parse_known_args()[0]
    return args

args=get_args()

device = "cuda" if torch.cuda.is_available() else "cpu"

# environments
env, train_envs, test_envs = make_telemetry_env(1, 1)

seed = args.seed

if torch.cuda.is_available():
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

node_num = env.observation_space.shape[0]
feature_num = env.observation_space.shape[1]
hidden_sizes = (64, 64)
activation = nn.ReLU

state_shape = env.observation_space.shape
action_shape = env.action_space.n

# create gcn
out_feature_num = 1 # Ensure that the state space does not increase excessively when the network scale becomes too large
gcn = GCN(feature_num, out_feature_num)
    
# Actor is a Diffusion model
actor = GCNCategoricalActor(
    feature_num=out_feature_num,
    node_num=node_num,
    gcn=gcn,
    hidden_sizes=hidden_sizes,
    act_num=action_shape,
    activation=activation,
).to(device)

# optim = torch.optim.AdamW(actor.parameters(), lr=args.lr, weight_decay=args.wd)
optim = torch.optim.Adam(actor.parameters(), lr=args.lr)

# Setup logging
time_now = datetime.now().strftime('%b%d-%H%M%S')
log_path = os.path.join('log_convergence', 'algos', time_now)
# log_path = os.path.join('log_pg', time_now)
writer = SummaryWriter(log_path)
writer.add_text("args", str(args))
logger = TensorboardLogger(writer)

# PPO policy
dist = torch.distributions.Categorical
policy = TelemetryPG(
    model=actor,
    optim=optim,
    env=env,
    device=device,
    dist_fn=dist,
    discount_factor=0.95,
    action_space=env.action_space,
    action_scaling=isinstance(env.action_space, Box),
    # reward_normalization=True,
)

# collector
train_collector = Collector(policy, train_envs, VectorReplayBuffer(args.buffer_size, len(train_envs)), exploration_noise=True)
test_collector = path_Collector(policy, test_envs, exploration_noise=True)

# trainer
result, best = TelemetryTrainer(
    policy=policy,
    batch_size=args.batch_size,
    train_collector=train_collector,
    test_collector=test_collector,
    max_epoch=args.epoch,
    step_per_epoch=args.step_per_epoch,
    repeat_per_collect=args.repeat_per_collect,
    episode_per_test=args.episode_per_test,
    step_per_collect=args.step_per_collect,
    episode_per_collect=args.episode_per_collect,
    logger = logger,
).run()
print(result)
print(best)
writer.add_text("best_probe_path", str(best)+','+result['best_result'])
print("-------------------------------------------------------")
# Let's watch its performance!
policy.eval()
# result = test_collector.collect(n_episode=1)
# print("Final reward: {}, length: {}".format(result["rews"].mean(), result["lens"].mean()))

probe_path_collector = path_Collector(policy, test_envs)
probe_path = probe_path_collector.collect(n_episode=1)
print("Final reward: {}, length: {}".format(probe_path["rews"].mean(), probe_path["lens"].mean()))
print(probe_path["probe_path"])
