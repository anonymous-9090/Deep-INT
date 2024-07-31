from typing import Any, Dict, List, Type, Optional, Union

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn
from copy import deepcopy

from tianshou.data import Batch, ReplayBuffer, to_torch, to_torch_as, to_numpy
from tianshou.policy import BasePolicy
from tianshou.utils import RunningMeanStd
from tianshou.utils.net.common import ActorCritic
from torch.distributions.categorical import Categorical
from torch.optim.lr_scheduler import CosineAnnealingLR

class TelemetryPG(BasePolicy):
    def __init__(
        self,
        model: torch.nn.Module,
        optim: torch.optim.Optimizer,
        env,
        device: torch.device,
        dist_fn: Type[torch.distributions.Distribution],
        discount_factor: float = 0.99,
        reward_normalization: bool = False,
        action_scaling: bool = True,
        action_bound_method: str = "clip",
        deterministic_eval: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            action_scaling=action_scaling,
            action_bound_method=action_bound_method,
            **kwargs
        )
        self.actor = model
        self.optim = optim
        self.dist_fn = dist_fn
        assert 0.0 <= discount_factor <= 1.0, "discount factor should be in [0, 1]"
        self._gamma = discount_factor
        self._rew_norm = reward_normalization
        self.ret_rms = RunningMeanStd()
        self._eps = 1e-8
        self._deterministic_eval = deterministic_eval

        self._device = device  # Device to run computations on
        self.env = env
        self.edge_index = deepcopy(self.env.edge_index)
        self.edge_index = self.edge_index.to(device)
        
    def process_fn(
        self, batch: Batch, buffer: ReplayBuffer, indices: np.ndarray
    ) -> Batch:
        r"""Compute the discounted returns for each transition.

        .. math::
            G_t = \sum_{i=t}^T \gamma^{i-t}r_i

        where :math:`T` is the terminal time step, :math:`\gamma` is the
        discount factor, :math:`\gamma \in [0, 1]`.
        """
        v_s_ = np.full(indices.shape, self.ret_rms.mean)
        unnormalized_returns, _ = self.compute_episodic_return(
            batch, buffer, indices, v_s_=v_s_, gamma=self._gamma, gae_lambda=1.0
        )
        if self._rew_norm:
            batch.returns = (unnormalized_returns - self.ret_rms.mean) / \
                np.sqrt(self.ret_rms.var + self._eps)
            self.ret_rms.update(unnormalized_returns)
        else:
            batch.returns = unnormalized_returns
        return batch

    def forward(
        self,
        batch: Batch,
        state: Optional[Union[dict, Batch, np.ndarray]] = None,
        **kwargs: Any,
    ) -> Batch:
        """Compute action over the given batch data.

        :return: A :class:`~tianshou.data.Batch` which has 4 keys:

            * ``act`` the action.
            * ``logits`` the network's raw output.
            * ``dist`` the action distribution.
            * ``state`` the hidden state.

        .. seealso::

            Please refer to :meth:`~tianshou.policy.BasePolicy.forward` for
            more detailed explanation.
        """
        obs_tem = to_torch(batch.obs, device=self._device, dtype=torch.float32) #转化为tensor，GCN层需要
        logits, hidden = self.actor.get_logits(obs_tem, self.edge_index), None
        mask = to_torch(batch['info'].mask, device=self._device)
        
        pi = Categorical(logits=logits)
        mask = torch.squeeze(mask)
        logits_delta = torch.zeros(mask.size()).to(mask.device)
        logits_delta[mask == 0] = float("-Inf")
        logits_ = logits + logits_delta
        pi_mask = Categorical(logits = logits_)
        
        a = pi_mask.sample()
        
        acts = a
        dist = pi  # does not use a probability distribution for actions
       
        if self._deterministic_eval and not self.training:
            if self.action_type == "discrete":
                act = logits.argmax(-1)
            elif self.action_type == "continuous":
                act = logits[0]
        else:
            act = dist.sample()
            
        return Batch(logits=logits, act=acts, state=hidden, dist=dist)

    def learn(  # type: ignore
        self, batch: Batch, batch_size: int, repeat: int, **kwargs: Any
    ) -> Dict[str, List[float]]:
        losses = []
        for _ in range(repeat):
            for minibatch in batch.split(batch_size, merge_last=True):
                self.optim.zero_grad()
                result = self(minibatch)
                dist = result.dist
                act = to_torch_as(minibatch.act, result.act)
                ret = to_torch(minibatch.returns, torch.float, result.act.device)
                log_prob = dist.log_prob(act).reshape(len(ret), -1).transpose(0, 1)
                loss = -(log_prob * ret).mean()
                loss.backward()
                self.optim.step()
                losses.append(loss.item())

        return {"loss": losses}