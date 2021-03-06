import math
import torch
from .optimizer import Optimizer


class Adam(Optimizer):
    """实现 Adam 算法。

    它在 `Adam: A Method for Stochastic Optimization`_ 中被提出.

    参数:
        params (iterable): 迭代的优化参数或者以字典的形式定义参数组.
        lr (float, optional): 学习率 (默认值: 1e-3)
        betas (Tuple[float, float], optional): 用来计算梯度和平方梯度的系数 (默认值: (0.9, 0.999))
        eps (float, optional): 增加分母来确保数值稳定性 (默认值: 1e-8)
        weight_decay (float, optional): 权重衰减 (L2 正则化) (默认值: 0)

    .. _Adam\: A Method for Stochastic Optimization:
        https://arxiv.org/abs/1412.6980
    """

    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8,
                 weight_decay=0):
        defaults = dict(lr=lr, betas=betas, eps=eps,
                        weight_decay=weight_decay)
        super(Adam, self).__init__(params, defaults)

    def step(self, closure=None):
        """进行单步优化.

        参数:
            closure (callable, optional): 一个重新评价模型并返回误差的闭包.
        """
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.is_sparse:
                    raise RuntimeError('Adam does not support sparse gradients, please consider SparseAdam instead')

                state = self.state[p]

                # State initialization
                if len(state) == 0:
                    state['step'] = 0
                    # Exponential moving average of gradient values
                    state['exp_avg'] = torch.zeros_like(p.data)
                    # Exponential moving average of squared gradient values
                    state['exp_avg_sq'] = torch.zeros_like(p.data)

                exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']
                beta1, beta2 = group['betas']

                state['step'] += 1

                if group['weight_decay'] != 0:
                    grad = grad.add(group['weight_decay'], p.data)

                # Decay the first and second moment running average coefficient
                exp_avg.mul_(beta1).add_(1 - beta1, grad)
                exp_avg_sq.mul_(beta2).addcmul_(1 - beta2, grad, grad)

                denom = exp_avg_sq.sqrt().add_(group['eps'])

                bias_correction1 = 1 - beta1 ** state['step']
                bias_correction2 = 1 - beta2 ** state['step']
                step_size = group['lr'] * math.sqrt(bias_correction2) / bias_correction1

                p.data.addcdiv_(-step_size, exp_avg, denom)

        return loss
