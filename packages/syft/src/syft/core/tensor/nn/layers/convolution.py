# stdlib
from typing import Dict
from typing import Optional
from typing import Tuple

# third party
import numpy as np

# relative
from .. import activations
from ....common.serde.serializable import serializable
from ...autodp.phi_tensor import PhiTensor
from ..initializations import XavierInitialization
from ..utils import col2im_indices
from ..utils import im2col_indices
from .base import Layer


@serializable(recursive_serde=True)
class Convolution(Layer):
    """
    If this is the first layer in a model, provide the keyword argument `input_shape`
    (tuple of integers, does NOT include the sample axis, N.),
    e.g. `input_shape=(3, 128, 128)` for 128x128 RGB pictures.
    """

    __attr_allowlist__ = [
        "nb_filter",
        "filter_size",
        "input_shape",
        "stride",
        "padding",
        "W",
        "b",
        "dW",
        "db",
        "out_shape",
        "last_output",
        "last_input",
        "init",
        "activation",
    ]

    def __init__(
        self,
        nb_filter,
        filter_size,
        input_shape: Optional[Tuple] = None,
        stride: int = 1,
        padding: int = 0,
        activation: Optional[activations.Activation] = None,
    ):
        self.nb_filter = nb_filter
        self.filter_size = filter_size
        self.input_shape = input_shape
        self.stride = stride
        self.padding = padding

        self.W, self.dW = None, None
        self.b, self.db = None, None
        self.out_shape = None
        self.last_output = None
        self.last_input = None
        self.X_col = None

        self.init = XavierInitialization()
        self.activation = activations.get(activation)

    def connect_to(self, prev_layer: Optional[Layer] = None):
        if prev_layer is None:
            assert self.input_shape is not None
            input_shape = self.input_shape
        else:
            input_shape = prev_layer.out_shape

        # input_shape: (batch size, num input feature maps, image height, image width)
        assert len(input_shape) == 4

        nb_batch, pre_nb_filter, pre_height, pre_width = input_shape
        if isinstance(self.filter_size, tuple):
            filter_height, filter_width = self.filter_size
        elif isinstance(self.filter_size, int):
            filter_height = filter_width = self.filter_size
        else:
            raise NotImplementedError

        height = (pre_height - filter_height + 2 * self.padding) // self.stride + 1
        width = (pre_width - filter_width + 2 * self.padding) // self.stride + 1

        # output shape
        self.out_shape = (nb_batch, self.nb_filter, height, width)

        # filters
        self.W = self.init((self.nb_filter, pre_nb_filter, filter_height, filter_width))
        self.b = np.zeros((self.nb_filter,))

    def forward(self, input: PhiTensor, *args: Tuple, **kwargs: Dict):
        # print("Input into Conv forward:", input.shape, input.data_subjects.shape)
        self.last_input = input

        n_filters, d_filter, h_filter, w_filter = self.W.shape

        n_x, d_x, h_x, w_x = input.shape

        (
            _,
            _,
            h_out,
            w_out,
        ) = self.out_shape

        self.ds_cached = input.data_subjects
        self.X_col = im2col_indices(
            input, h_filter, w_filter, padding=self.padding, stride=self.stride
        )
        # print("X_col after im2col", self.X_col.shape, self.X_col.data_subjects.shape)

        # relative
        from ...autodp.gamma_tensor import GammaTensor

        # if isinstance(self.W, (PhiTensor, GammaTensor)):
        #     print("W", self.W.shape, self.W.data_subjects.shape)
        W_col = self.W.reshape((n_filters, -1))
        # if isinstance(self.W, (PhiTensor, GammaTensor)):
        #     print("W after reshape", W_col.shape, W_col.data_subjects.shape)
        out = (
            self.X_col.T @ W_col.T + self.b
        )  # Transpose is required here because W_col is numpy array
        # print("out after matmul", out.shape, out.data_subjects.shape)
        out = out.reshape((n_filters, h_out, w_out, n_x))
        # print("out after reshape", out.shape, out.data_subjects.shape)
        out = out.transpose((3, 0, 1, 2))
        # print("out after transpose", out.shape, out.data_subjects.shape)

        self.last_output = (
            self.activation.forward(out) if self.activation is not None else out
        )
        # print(
        #     "out after matmul",
        #     self.last_output.shape,
        #     self.last_output.data_subjects.shape,
        # )
        # print("Done with convolution")
        return out

    def backward(self, pre_grad: PhiTensor, *args: Tuple, **kwargs: Dict):
        n_filter, d_filter, h_filter, w_filter = self.W.shape

        pre_grads = (
            (pre_grad * self.activation.derivative(pre_grad))
            if self.activation is not None
            else pre_grad
        )
        print("pre_grads ", pre_grad.shape, pre_grads.min_vals.shape)
        db = pre_grads.sum(axis=(0, 2, 3))
        print("db ", db.shape, db.min_vals.shape)
        self.db = db.reshape((n_filter, -1))
        self.db.min_vals.shape = self.db.max_vals.shape = self.db.shape
        print("self db ", self.db.shape, self.db.min_vals.shape)

        pre_grads_reshaped = pre_grads.transpose((1, 2, 3, 0))
        print("pre_grads ", pre_grads_reshaped.shape, pre_grads_reshaped.min_vals.shape)
        pre_grads_reshaped = pre_grads_reshaped.reshape((n_filter, -1))
        pre_grads_reshaped.min_vals.shape = pre_grads_reshaped.max_vals.shape = pre_grads_reshaped.shape
        print("pre_grads ", pre_grads_reshaped.shape, pre_grads_reshaped.min_vals.shape)
        print("X_cols", self.X_col.shape, self.X_col.min_vals.shape)
        dW = pre_grads_reshaped @ self.X_col.T
        self.dW = dW.reshape(self.W.shape)

        W_reshape = self.W.reshape(n_filter, -1)
        print("W_reshape, ", W_reshape.shape)
        # W_reshape.min_vals.shape = W_reshape.max_vals.shape = W_reshape.shape
        dX_col = pre_grads_reshaped.T @ W_reshape
        print("dX_col ", dX_col.shape)
        dX = col2im_indices(
            dX_col,
            self.input_shape,
            self.ds_cached,
            h_filter,
            w_filter,
            padding=self.padding,
            stride=self.stride,
        )
        return dX

    @property
    def params(self):
        return self.W, self.b

    @params.setter
    def params(self, new_params):
        assert (
            len(new_params) == 2
        ), f"Expected Two values Update Params has length{len(new_params)}"
        self.W, self.b = new_params

    @property
    def grads(self):
        return self.dW, self.db
